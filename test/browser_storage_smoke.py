"""Opt-in Chromium storage/import UI checks; see docs/cloud-storage-smoke.md."""

from contextlib import ExitStack
import json
from pathlib import Path
import select
import shutil
import subprocess
import unittest

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
STORAGE_KEY = "spam-calls-synthetic-demo-v1"


class StorageUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resources = ExitStack()
        cls.addClassCleanup(cls.resources.close)
        # Use the real allowlisted server on an OS-selected loopback port.
        cls.server = subprocess.Popen(
            ["node", "--input-type=module", "-e",
             "import { createServer } from './scripts/serve.mjs'; "
             "const server = createServer(); "
             "server.listen(0, '127.0.0.1', () => console.log(server.address().port));"],
            cwd=ROOT, stdout=subprocess.PIPE, text=True,
        )
        cls.resources.callback(cls.stop_server)
        if not select.select([cls.server.stdout], [], [], 10)[0]:
            raise RuntimeError("Loopback test server did not start within 10 seconds")
        cls.origin = f"http://127.0.0.1:{int(cls.server.stdout.readline())}"
        chromium = shutil.which("chromium") or shutil.which("google-chrome")
        if not chromium:
            raise RuntimeError("Install/provide Chromium separately; this test installs nothing")
        cls.playwright = cls.resources.enter_context(sync_playwright())
        cls.browser = cls.playwright.chromium.launch(executable_path=chromium, headless=True)
        cls.resources.callback(cls.browser.close)
        print(f"Storage UI smoke: Chromium {cls.browser.version}; headless synthetic checks only", flush=True)

    @classmethod
    def stop_server(cls):
        cls.server.terminate()
        try:
            cls.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.server.kill()
            cls.server.wait(timeout=5)
        cls.server.stdout.close()

    def setUp(self):
        # Never attach to a running browser or its persistent profile.
        self.context = self.browser.new_context(service_workers="block")
        self.addCleanup(self.context.close)
        self.unexpected_requests = []
        self.page_errors = []

        def allow_loopback(route):
            if route.request.url.startswith(self.origin + "/"):
                route.continue_()
            else:
                self.unexpected_requests.append(route.request.url)
                route.abort()

        self.context.route("**/*", allow_loopback)
        self.page = self.context.new_page()
        self.page.on("pageerror", lambda error: self.page_errors.append(str(error)))

    def tearDown(self):
        self.assertEqual(self.page_errors, [], "Unhandled browser error")
        self.assertEqual(self.unexpected_requests, [], "Unexpected non-test-origin request")

    def open_app(self, setup=""):
        if setup:
            self.context.add_init_script(setup)
        self.page.goto(self.origin)
        expect(self.page.locator("#broker-name")).to_have_text("Cedar Directory")

    def submit(self, event="submission"):
        self.page.locator("#identity").select_option("demo-a")
        self.page.locator("#event").select_option(event)
        self.page.locator("#artifact").select_option(f"cedar-{event}")
        self.page.locator("#approval").check()
        self.page.get_by_role("button", name="Record simulated event").click()

    def exported_events(self):
        self.page.get_by_role("button", name="Preview export").click()
        result = json.loads(self.page.locator("#data-text").input_value())["events"]
        self.page.get_by_role("button", name="Cancel", exact=True).click()
        return result

    def assert_storage_unavailable(self):
        expect(self.page.get_by_role("button", name="Record simulated event")).to_be_disabled()
        expect(self.page.locator("#identity")).to_be_disabled()
        expect(self.page.get_by_role("button", name="Preview export")).to_be_disabled()
        expect(self.page.get_by_role("button", name="Import demo")).to_be_disabled()
        expect(self.page.locator("#persistence")).to_contain_text("Local storage unavailable")

    def import_payload(self, before):
        # Add one known fixture event to the history recorded through the UI.
        # Equal timestamps are valid; this avoids relying on the runner's date.
        return {"schemaVersion": 1, "fixtureSet": "demo-v1", "events": [*before, {
            "schemaVersion": 1, "id": "event-import-awaiting",
            "timestamp": before[0]["timestamp"], "caseId": "demo-a",
            "brokerId": "cedar", "identity": "demo-a", "approved": True,
            "type": "awaiting", "artifactId": "cedar-awaiting", "supersedes": None,
        }]}

    def preview_import(self, payload):
        self.page.get_by_role("button", name="Import demo").click()
        self.page.locator("#data-text").fill(json.dumps(payload))
        self.page.get_by_role("button", name="Preview import", exact=True).click()
        expect(self.page.locator("#dialog-message")).to_have_text(
            "Validated preview: 2 total synthetic events after import. Existing history is still unchanged.")
        expect(self.page.get_by_role("button", name="Apply validated import")).to_be_visible()
        self.assertEqual(json.loads(self.page.locator("#data-text").input_value()), payload)

    def stored_text(self):
        return self.page.evaluate(f"localStorage.getItem({json.dumps(STORAGE_KEY)})")

    def assert_submission_visible(self):
        expect(self.page.locator("#item-status")).to_contain_text("Simulated status: simulated-submission.")
        expect(self.page.locator("#timeline li")).to_have_count(1)
        expect(self.page.locator("#timeline li strong")).to_have_text("Simulated submission")

    def assert_import_applied(self, payload):
        expect(self.page.locator("#data-dialog")).not_to_be_visible()
        expect(self.page.locator("#message")).to_have_text(
            "Validated synthetic history imported. Duplicate events were kept once.")
        expect(self.page.locator("#item-status")).to_contain_text("Simulated status: awaiting-simulated-confirmation.")
        expect(self.page.locator("#timeline li strong")).to_have_text([
            "Simulated submission", "Await simulated confirmation",
        ])
        self.assertEqual(self.exported_events(), payload["events"])

    def fail_storage_writes(self):
        # Fault injection stays at the browser storage boundary, not app internals.
        self.page.evaluate("""() => {
            Storage.prototype.setItem = function() {
                throw new DOMException('Synthetic quota exceeded', 'QuotaExceededError');
            };
        }""")

    def test_corrupt_storage_requires_explicit_reset_and_recovers(self):
        # Seed only this disposable context; the app is responsible for recovery.
        self.open_app(f"localStorage.setItem({json.dumps(STORAGE_KEY)}, '{{broken');")
        self.assert_storage_unavailable()
        expect(self.page.locator("#message")).to_contain_text("Existing data was not replaced")
        self.page.get_by_role("button", name="Reset demo", exact=True).click()
        self.page.get_by_role("button", name="Keep history").click()
        self.assertEqual(self.page.evaluate(f"localStorage.getItem({json.dumps(STORAGE_KEY)})"), "{broken")
        self.assert_storage_unavailable()
        self.page.get_by_role("button", name="Reset demo", exact=True).click()
        self.page.get_by_role("button", name="Reset all demo history").click()
        expect(self.page.locator("#message")).to_contain_text("All demo history reset")
        self.assertEqual(self.exported_events(), [])
        self.submit()
        expect(self.page.locator("#message")).to_contain_text("Simulated event saved")
        self.assertEqual(len(self.exported_events()), 1)

    def test_unavailable_storage_reports_failure_including_reset(self):
        self.open_app("Object.defineProperty(window, 'localStorage', {get() {"
                      "throw new DOMException('Synthetic storage denied', 'SecurityError'); }});")
        self.assert_storage_unavailable()
        expect(self.page.locator("#message")).to_contain_text("Synthetic storage denied")
        self.page.get_by_role("button", name="Reset demo", exact=True).click()
        self.page.get_by_role("button", name="Reset all demo history").click()
        expect(self.page.locator("#reset-dialog")).not_to_be_visible()
        expect(self.page.locator("#message")).to_have_text("Synthetic storage denied")
        self.assert_storage_unavailable()

    def test_failed_write_preserves_history_and_can_retry(self):
        self.open_app()
        self.submit()
        expect(self.page.locator("#message")).to_contain_text("Simulated event saved")
        before = self.exported_events()
        self.assertEqual(len(before), 1)
        self.fail_storage_writes()
        self.submit("awaiting")
        expect(self.page.locator("#message")).to_have_text("Synthetic quota exceeded")
        expect(self.page.locator("#approval")).not_to_be_checked()
        expect(self.page.get_by_role("button", name="Record simulated event")).to_be_enabled()
        self.assert_submission_visible()
        self.assertEqual(self.exported_events(), before)
        self.page.reload()  # removes the injected failure and reopens persisted history
        expect(self.page.locator("#broker-name")).to_have_text("Cedar Directory")
        self.assertEqual(self.exported_events(), before)
        self.submit("awaiting")
        expect(self.page.locator("#message")).to_contain_text("Simulated event saved")
        expect(self.page.locator("#item-status")).to_contain_text("Simulated status: awaiting-simulated-confirmation.")
        expect(self.page.locator("#timeline li strong")).to_have_text([
            "Simulated submission", "Await simulated confirmation",
        ])
        events = self.exported_events()
        self.assertEqual([event["type"] for event in events], ["submission", "awaiting"])
        self.assertEqual(events[0], before[0])

    def test_import_preview_cancel_apply_and_repeat(self):
        self.open_app()
        self.submit()
        expect(self.page.locator("#message")).to_contain_text("Simulated event saved")
        before = self.exported_events()
        payload = self.import_payload(before)
        saved = self.stored_text()
        self.preview_import(payload)
        self.assert_submission_visible()
        self.assertEqual(self.stored_text(), saved)
        self.page.get_by_role("button", name="Cancel", exact=True).click()
        self.assertEqual(self.exported_events(), before)
        self.page.reload()
        self.assertEqual(self.exported_events(), before)
        self.preview_import(payload)
        self.page.get_by_role("button", name="Apply validated import").click()
        self.assert_import_applied(payload)
        self.page.reload()
        self.assertEqual(self.exported_events(), payload["events"])
        # Repeating the identical import must retain the exact history once.
        self.preview_import(payload)
        self.page.get_by_role("button", name="Apply validated import").click()
        self.assert_import_applied(payload)
        self.page.reload()
        self.assertEqual(self.exported_events(), payload["events"])

    def test_import_edit_invalidates_preview_and_errors_allow_recovery(self):
        self.open_app()
        self.submit()
        expect(self.page.locator("#message")).to_contain_text("Simulated event saved")
        before = self.exported_events()
        payload = self.import_payload(before)
        saved = self.stored_text()
        self.preview_import(payload)
        for text, error in (
            ("{broken", "Invalid synthetic JSON. Nothing was changed."),
            (json.dumps({**payload, "unknown": True}), "State has unknown or missing fields."),
        ):
            with self.subTest(error=error):
                self.page.locator("#data-text").fill(text)
                expect(self.page.get_by_role("button", name="Preview import", exact=True)).to_be_visible()
                expect(self.page.locator("#dialog-message")).to_be_empty()
                self.page.get_by_role("button", name="Preview import", exact=True).click()
                expect(self.page.locator("#dialog-message")).to_have_text(error)
                expect(self.page.locator("#data-dialog")).to_be_visible()
                self.assert_submission_visible()
                self.assertEqual(self.stored_text(), saved)
        self.page.get_by_role("button", name="Cancel", exact=True).click()
        self.assertEqual(self.exported_events(), before)
        self.preview_import(payload)
        self.page.get_by_role("button", name="Apply validated import").click()
        self.assert_import_applied(payload)
        self.page.reload()
        self.assertEqual(self.exported_events(), payload["events"])

    def test_import_write_failure_requires_new_preview_and_preserves_history(self):
        self.open_app()
        self.submit()
        expect(self.page.locator("#message")).to_contain_text("Simulated event saved")
        before = self.exported_events()
        payload = self.import_payload(before)
        saved = self.stored_text()
        self.preview_import(payload)
        self.fail_storage_writes()
        self.page.get_by_role("button", name="Apply validated import").click()
        expect(self.page.locator("#dialog-message")).to_have_text("Synthetic quota exceeded")
        expect(self.page.locator("#data-dialog")).to_be_visible()
        expect(self.page.get_by_role("button", name="Preview import", exact=True)).to_be_visible()
        self.assert_submission_visible()
        self.assertEqual(self.stored_text(), saved)
        self.page.get_by_role("button", name="Cancel", exact=True).click()
        self.assertEqual(self.exported_events(), before)
        self.page.reload()  # clears the fault injection, preserving only actual saved data
        self.assertEqual(self.exported_events(), before)
        self.preview_import(payload)
        self.page.get_by_role("button", name="Apply validated import").click()
        self.assert_import_applied(payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
