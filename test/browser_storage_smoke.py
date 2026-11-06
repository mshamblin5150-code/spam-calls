"""Opt-in synthetic UI checks; see docs/cloud-storage-smoke.md and docs/dialog-pointer-exclusion.md."""

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

    def test_390px_keyboard_submission_rejects_mismatch_and_requires_fresh_approval(self):
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.open_app()
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), 390)
        self.assertIsNone(self.stored_text())
        self.page.evaluate("""() => {
            window.invalidControls = [];
            document.addEventListener('invalid', event => {
                window.invalidControls.push({id: event.target.id, trusted: event.isTrusted});
            }, {capture: true, passive: true});
        }""")

        def key_to(key, selector):
            self.page.keyboard.press(key)
            expect(self.page.locator(selector)).to_be_focused()
            expect(self.page.locator(selector)).to_be_in_viewport()

        # Real keyboard input from initial document focus; no click/focus shortcut.
        for selector in ["#export", "#import", "#reset", "#case",
                         "#brokers .broker:nth-child(1)", "#brokers .broker:nth-child(2)",
                         "#identity"]:
            key_to("Tab", selector)
        self.page.keyboard.press("End")  # Demo Case B mismatches selected Case A.
        expect(self.page.locator("#identity")).to_have_value("demo-b")
        key_to("Tab", "#event")
        key_to("Tab", "#artifact")
        self.page.keyboard.press("End")
        expect(self.page.locator("#artifact")).to_have_value("cedar-submission")
        key_to("Tab", "#approval")
        self.page.keyboard.press("Space")
        expect(self.page.locator("#approval")).to_be_checked()
        key_to("Tab", "#event-form button[type=submit]")
        self.page.keyboard.press("Enter")
        expect(self.page.locator("#message")).to_have_text("Select the matching demo identity.")
        expect(self.page.locator("#approval")).not_to_be_checked()
        self.assertIsNone(self.stored_text())
        expect(self.page.locator("#timeline li")).to_have_text("No simulated events yet.")

        for selector in ["#approval", "#artifact", "#event", "#identity"]:
            key_to("Shift+Tab", selector)
        self.page.keyboard.press("Home")
        self.page.keyboard.press("ArrowDown")
        expect(self.page.locator("#identity")).to_have_value("demo-a")
        for selector in ["#event", "#artifact", "#approval", "#event-form button[type=submit]"]:
            key_to("Tab", selector)
        # Correct identity still cannot save with the consumed approval unchecked.
        self.page.keyboard.press("Enter")
        expect(self.page.locator("#approval")).to_be_focused()
        self.assertEqual(self.page.evaluate("window.invalidControls"),
                         [{"id": "approval", "trusted": True}])
        self.assertIsNone(self.stored_text())
        expect(self.page.locator("#timeline li")).to_have_text("No simulated events yet.")

        self.page.keyboard.press("Space")
        expect(self.page.locator("#approval")).to_be_checked()
        key_to("Tab", "#event-form button[type=submit]")
        self.page.keyboard.press("Enter")
        self.assert_submission_visible()
        expect(self.page.locator("#identity")).to_have_value("")
        expect(self.page.locator("#approval")).not_to_be_checked()
        saved = json.loads(self.stored_text())["events"]
        self.assertEqual(len(saved), 1)
        self.assertEqual((saved[0]["caseId"], saved[0]["identity"], saved[0]["approved"]),
                         ("demo-a", "demo-a", True))
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), 390)
        self.page.reload()
        self.assert_submission_visible()
        self.assertEqual(json.loads(self.stored_text())["events"], saved)

    def test_form_context_changes_clear_one_use_approval(self):
        self.open_app()
        changes = [
            ("identity", lambda: self.page.locator("#identity").select_option("demo-b")),
            ("event", lambda: self.page.locator("#event").select_option("awaiting")),
            ("evidence", lambda: self.page.locator("#artifact").select_option("")),
            ("case", lambda: self.page.locator("#case").select_option("demo-b")),
            ("broker", lambda: self.page.locator("#brokers .broker:nth-child(2)").click()),
        ]
        for context, change in changes:
            with self.subTest(context=context):
                self.page.locator("#case").select_option("demo-a")
                self.page.locator("#brokers .broker:nth-child(1)").click()
                self.page.locator("#identity").select_option("demo-a")
                self.page.locator("#event").select_option("submission")
                self.page.locator("#artifact").select_option("cedar-submission")
                self.page.locator("#approval").check()
                expect(self.page.locator("#approval")).to_be_checked()
                change()
                expect(self.page.locator("#approval")).not_to_be_checked()
                self.assertIsNone(self.stored_text())
                expect(self.page.locator("#timeline li")).to_have_text("No simulated events yet.")

    def test_valid_history_reset_cancel_confirm_reload_and_reopen(self):
        self.open_app()
        self.submit()
        self.assert_submission_visible()
        self.submit("awaiting")
        expect(self.page.locator("#item-status")).to_contain_text(
            "Simulated status: awaiting-simulated-confirmation.")
        expect(self.page.locator("#timeline li strong")).to_have_text([
            "Simulated submission", "Await simulated confirmation",
        ])
        before = self.stored_text()
        self.assertEqual([event["type"] for event in json.loads(before)["events"]],
                         ["submission", "awaiting"])
        # This extra synthetic key belongs only to the fresh disposable context.
        sentinel_key = "synthetic-reset-unrelated"
        sentinel_value = "keep-this-synthetic-value"
        self.page.evaluate("([key, value]) => localStorage.setItem(key, value)",
                           [sentinel_key, sentinel_value])

        def assert_empty_history():
            expect(self.page.locator("#item-status")).to_contain_text("Simulated status: planned.")
            expect(self.page.locator("#timeline li")).to_have_count(1)
            expect(self.page.locator("#timeline li")).to_have_text("No simulated events yet.")
            self.assertEqual(self.exported_events(), [])

        def stored_values():
            return self.page.evaluate("() => Object.fromEntries(Object.entries(localStorage))")

        self.page.get_by_role("button", name="Reset demo", exact=True).click()
        expect(self.page.locator("#reset-dialog")).to_be_visible()
        self.page.get_by_role("button", name="Keep history").click()
        expect(self.page.locator("#reset-dialog")).not_to_be_visible()
        self.assertEqual(stored_values(), {STORAGE_KEY: before, sentinel_key: sentinel_value})
        expect(self.page.locator("#timeline li strong")).to_have_text([
            "Simulated submission", "Await simulated confirmation",
        ])

        self.page.get_by_role("button", name="Reset demo", exact=True).click()
        self.page.get_by_role("button", name="Reset all demo history").click()
        expect(self.page.locator("#reset-dialog")).not_to_be_visible()
        expect(self.page.locator("#message")).to_have_text(
            "All demo history reset. No external data was changed.")
        assert_empty_history()
        empty_bytes = self.stored_text()
        self.assertEqual(json.loads(empty_bytes),
                         {"schemaVersion": 1, "fixtureSet": "demo-v1", "events": []})
        self.assertEqual(stored_values(), {STORAGE_KEY: empty_bytes, sentinel_key: sentinel_value})

        self.page.reload()
        assert_empty_history()
        self.assertEqual(stored_values(), {STORAGE_KEY: empty_bytes, sentinel_key: sentinel_value})
        self.page.get_by_role("button", name="Reset demo", exact=True).click()
        expect(self.page.locator("#reset-dialog")).to_be_visible()
        self.page.get_by_role("button", name="Keep history").click()
        expect(self.page.locator("#reset-dialog")).not_to_be_visible()
        assert_empty_history()
        self.assertEqual(stored_values(), {STORAGE_KEY: empty_bytes, sentinel_key: sentinel_value})

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

    def pointer_state(self):
        # Deliberately excludes activeElement, browser chrome, and native focus.
        return self.page.evaluate("""() => ({
            case: document.getElementById('case').value,
            broker: document.getElementById('broker-name').textContent,
            identity: document.getElementById('identity').value,
            event: document.getElementById('event').value,
            artifact: document.getElementById('artifact').value,
            approval: document.getElementById('approval').checked,
            timeline: document.getElementById('timeline').textContent,
            status: document.getElementById('item-status').textContent,
            stored: localStorage.getItem('spam-calls-synthetic-demo-v1'),
            modal: [...document.querySelectorAll('dialog:modal')].map(node => node.id),
        })""")

    def pointer_point(self, selector):
        control = self.page.locator(selector)
        expect(control).to_be_visible()
        expect(control).to_be_enabled()
        box = control.bounding_box()
        self.assertIsNotNone(box)
        point = {"x": box["x"] + box["width"] / 2, "y": box["y"] + box["height"] / 2}
        viewport = self.page.viewport_size
        self.assertTrue(0 < point["x"] < viewport["width"])
        self.assertTrue(0 < point["y"] < viewport["height"])
        return point

    def mouse_probe(self, point):
        self.page.evaluate("window.pointerProbeEvents.length = 0")
        self.page.mouse.click(point["x"], point["y"])
        events = self.page.evaluate("window.pointerProbeEvents")
        self.assertTrue(any(event["type"] == "pointerdown" and event["trusted"] for event in events), events)
        self.assertTrue(any(event["type"] == "click" and event["trusted"] for event in events), events)
        return events

    def assert_live_pointer(self, selector, point):
        events = self.mouse_probe(point)
        self.assertTrue(any(event["type"] == "click" and event["trusted"]
                            and selector in event["controls"] for event in events), events)

    def modal_pointer_check(self, mode):
        # A wide viewport keeps every tested target center outside the dialog box.
        # These are CSS viewport coordinates, not a desktop/native-window probe.
        self.page.set_viewport_size({"width": 2000, "height": 1600})
        self.open_app()
        self.submit()
        expect(self.page.locator("#message")).to_contain_text("Simulated event saved")
        original = self.exported_events()
        self.assertEqual(len(original), 1)
        # If a background submit leaks, this valid command would append an event.
        self.page.locator("#identity").select_option("demo-a")
        self.page.locator("#event").select_option("issue")
        self.page.locator("#artifact").select_option("cedar-issue")
        self.page.locator("#approval").check()
        selectors = ["#export", "#brokers .broker:nth-child(2)", "#approval", "#event-form button[type=submit]"]
        if mode == "export":
            selectors.append("#reset")
        points = {selector: self.pointer_point(selector) for selector in selectors}
        # Passive capture observers never cancel, dispatch, or activate events.
        self.page.evaluate("""selectors => {
            window.pointerProbeEvents = [];
            for (const type of ['pointerdown', 'pointerup', 'click', 'input', 'change']) {
                document.addEventListener(type, event => {
                    const node = event.target instanceof Element ? event.target : null;
                    window.pointerProbeEvents.push({
                        type: event.type, trusted: event.isTrusted,
                        controls: selectors.filter(selector => node?.closest(selector)),
                        dialog: node?.closest('dialog')?.id ?? null,
                    });
                }, {capture: true, passive: true});
            }
        }""", selectors)
        self.page.get_by_role("button", name={
            "export": "Preview export", "import": "Import demo", "reset": "Reset demo",
        }[mode], exact=True).click()
        dialog_id = "reset-dialog" if mode == "reset" else "data-dialog"
        dialog = self.page.locator("#" + dialog_id)
        expect(dialog).to_be_visible()
        self.assertTrue(dialog.evaluate("node => node.matches(':modal')"))
        before = self.pointer_state()
        self.assertEqual(before["modal"], [dialog_id])
        for selector, point in points.items():
            with self.subTest(mode=mode, background_control=selector):
                control = self.page.locator(selector)
                expect(control).to_be_visible()
                expect(control).to_be_enabled()
                current = control.bounding_box()
                rectangle = dialog.bounding_box()
                self.assertIsNotNone(current)
                self.assertIsNotNone(rectangle)
                self.assertTrue(current["x"] < point["x"] < current["x"] + current["width"]
                                and current["y"] < point["y"] < current["y"] + current["height"],
                                "Recorded point no longer lies inside the current background control")
                self.assertFalse(rectangle["x"] <= point["x"] <= rectangle["x"] + rectangle["width"]
                                 and rectangle["y"] <= point["y"] <= rectangle["y"] + rectangle["height"],
                                 "Target center is covered by the dialog, not an outside-dialog probe")
                events = self.mouse_probe(point)
                self.assertTrue(all(event["controls"] == [] for event in events), events)
                self.assertTrue(all(event["dialog"] == dialog_id for event in events), events)
                self.assertEqual(self.pointer_state(), before)

        cancel = "#cancel-reset" if mode == "reset" else "#close-dialog"
        self.page.mouse.click(**self.pointer_point(cancel))
        expect(dialog).not_to_be_visible()
        self.assertEqual(self.pointer_state()["modal"], [])
        # Each exact target must receive trusted input and perform its normal
        # action after cancellation; otherwise blocked probes could be vacuous.
        self.assert_live_pointer("#approval", points["#approval"])
        expect(self.page.locator("#approval")).not_to_be_checked()
        self.assert_live_pointer("#approval", points["#approval"])
        expect(self.page.locator("#approval")).to_be_checked()
        submit = "#event-form button[type=submit]"
        self.assert_live_pointer(submit, points[submit])
        expect(self.page.locator("#message")).to_contain_text("Simulated event saved")
        expect(self.page.locator("#item-status")).to_contain_text("Simulated status: unresolved.")
        history = json.loads(self.pointer_state()["stored"])["events"]
        self.assertEqual([event["type"] for event in history], ["submission", "issue"])
        self.assertEqual(history[0], original[0])
        broker = "#brokers .broker:nth-child(2)"
        self.assert_live_pointer(broker, points[broker])
        expect(self.page.locator("#broker-name")).to_have_text("Harbor Index")
        self.assert_live_pointer("#export", points["#export"])
        expect(self.page.locator("#data-title")).to_have_text("Preview synthetic export")
        self.assertTrue(self.page.locator("#data-dialog").evaluate("node => node.matches(':modal')"))
        self.page.mouse.click(**self.pointer_point("#close-dialog"))
        if mode == "export":
            saved = self.pointer_state()["stored"]
            self.assert_live_pointer("#reset", points["#reset"])
            self.assertEqual(self.pointer_state()["modal"], ["reset-dialog"])
            self.assertEqual(self.pointer_state()["stored"], saved)
            self.page.mouse.click(**self.pointer_point("#cancel-reset"))
            self.assertEqual(self.pointer_state()["modal"], [])
            self.assertEqual(self.pointer_state()["stored"], saved)
        count = len(selectors)
        print(f"Pointer-only {mode}: {count} background probes blocked with unchanged state; all {count} targets live after cancel", flush=True)

    def test_export_modal_excludes_tested_background_pointer_input(self):
        self.modal_pointer_check("export")

    def test_import_modal_excludes_tested_background_pointer_input(self):
        self.modal_pointer_check("import")

    def test_reset_modal_excludes_tested_background_pointer_input(self):
        self.modal_pointer_check("reset")


if __name__ == "__main__":
    unittest.main(verbosity=2)
