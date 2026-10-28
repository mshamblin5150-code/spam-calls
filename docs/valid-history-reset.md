# Valid-history Reset browser regression

This test-only slice starts from merged main
`a32c0203e8e531f8db4934f965cb194e4e737a1a`. Parent-requested coverage was missing:
existing browser checks covered corrupt-storage recovery, unavailable storage,
and Reset cancellation during pointer checks, but not confirming Reset on valid
history followed by reload and reopening Reset. No open repository issue or PR
and no active child worker duplicated this assignment at the initial check.

`StorageUI.test_valid_history_reset_cancel_confirm_reload_and_reopen` uses the
existing optional cloud harness: the real allowlisted server, fresh nonpersistent
context, blocked external requests and unhandled-page-error checks. It records a
submission and awaiting event through the UI and waits for their visible states.
An unrelated synthetic storage key belongs only to this disposable context.
The test checks:

- Keep history closes Reset and preserves exact demo bytes and both visible events.
- Confirming Reset displays the success message and empty planned history, replaces
  only the demo key with schema 1/demo-v1/empty events, and preserves the unrelated key.
- Reload retains empty history and exact storage values.
- Reopening Reset and choosing Keep history retains that empty history and storage.

Run the focused test with:

```sh
python test/browser_storage_smoke.py StorageUI.test_valid_history_reset_cancel_confirm_reload_and_reopen
```

Run all browser checks with `python test/browser_storage_smoke.py` and the Node
checks with `npm test`. No new dependencies or installation are required.

The initial focused test passed (1 test, 6.465s). The first full run failed after
reading storage before the second asynchronous seed save completed. The test now
waits for visible saved states before reading storage; that failure is retained
in ignored evidence. No application defect or product red/green fix is claimed.
The corrected full browser run passed all 10 tests in 20.734s on headless Chromium
154.0.8037.57; Node passed all 14 tests. Immutable review identities are supplied
in the handoff.

Provenance: installed Matt Pocock engineering/tdd (including tests.md and
mocking.md), engineering/code-review and engineering/pr; P-Stack
principle-prove-it-works. Public UI behavior plus the explicitly authorized
browser-storage boundary are the agreed test seams. Installed source pins remain
Matt Pocock `49dd158d1076134a641b33efb035946536778336` and P-Stack
`e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`.

No application, verifier, vendor, manifest, notice or dependency bytes change.
The verifier and full vendor inputs remain identical to the prior actual
PowerShell 7.6.9 gate: exit 0, 263 files. No PowerShell execution occurred for
this slice; the separate historical wrapper assertion failure remains retained.

This is headless cloud storage/reset evidence only. It does not establish native
keyboard/focus/reentry, accessibility behavior or full dialog acceptance. The
local loopback EACCES denial and earlier native-window denial remain untouched.
