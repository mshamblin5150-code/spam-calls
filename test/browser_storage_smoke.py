"""Opt-in Chromium storage UI checks; see docs/cloud-storage-smoke.md."""

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
        # Fault injection stays at the browser storage boundary, not app internals.
        self.page.evaluate("""() => {
            Storage.prototype.setItem = function() {
                throw new DOMException('Synthetic quota exceeded', 'QuotaExceededError');
            };
        }""")
        self.submit("awaiting")
        expect(self.page.locator("#message")).to_have_text("Synthetic quota exceeded")
        expect(self.page.locator("#approval")).not_to_be_checked()
        expect(self.page.get_by_role("button", name="Record simulated event")).to_be_enabled()
        expect(self.page.locator("#item-status")).to_contain_text("Simulated status: simulated-submission.")
        expect(self.page.locator("#timeline li")).to_have_count(1)
        expect(self.page.locator("#timeline li strong")).to_have_text("Simulated submission")
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
