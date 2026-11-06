# Bounded narrow-screen keyboard and approval checks

This test-only slice starts from merged main
`652099b584d74483a69926a083fc2fb0b1d13530`. The requested follow-up in
`docs/prototype-review.md` names repeatable approval clearing and 390px keyboard
operation. Earlier tests checked failed-write clearing and pointer behavior, but
not this keyboard workflow or all five form-context approval resets. No open
repository issue/PR or active child worker duplicated the slice at initial review.

The existing optional cloud harness runs the real allowlisted app with fresh
nonpersistent contexts, external requests blocked and unhandled errors checked.
Two new tests exercise the agreed public UI and browser-storage seams:

- At 390×844 CSS pixels, Tab from initial document focus traverses toolbar, case,
  broker buttons and form. Each expected target must be focused and intersect the
  viewport. End/Home/ArrowDown choose synthetic identity/evidence; Space approves;
  Enter submits. No pointer activation, programmatic focus or select-option helper
  is used in this keyboard workflow.
- A mismatched identity with approval produces the real validation error, clears
  approval and saves nothing. Correcting identity without approving again produces
  a trusted native invalid event for approval and still saves nothing. Checking
  approval then submitting saves exactly one matching synthetic event, clears
  identity/approval and survives reload. No horizontal overflow is observed before
  the workflow or after submission.
- A separate UI test re-arms approval before each identity, event, evidence, case
  and broker change; each change must clear approval without saving history. This
  test uses ordinary locator select/click/check helpers and makes no keyboard-only
  claim for those five changes.

Focused command:

```sh
python test/browser_storage_smoke.py \
  StorageUI.test_390px_keyboard_submission_rejects_mismatch_and_requires_fresh_approval \
  StorageUI.test_form_context_changes_clear_one_use_approval
```

Full checks: `python test/browser_storage_smoke.py` and `npm test`.
The initial two-test run passed in 9.161s before adding explicit viewport-intersection
and initial no-overflow assertions. The final full browser suite passed 12 tests
in 18.701s on headless Chromium 154.0.8037.57; Node passed 14 tests. Immutable
review identities are recorded in the handoff. This adds coverage of existing behavior; no product defect or product
red/green fix is claimed.

Provenance: installed Matt Pocock engineering/tdd, tests.md, mocking.md,
engineering/code-review and engineering/pr, plus P-Stack principle-prove-it-works.
Pinned sources remain Matt Pocock `49dd158d1076134a641b33efb035946536778336`
and P-Stack `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`.

No application, vendor, verifier, manifest, notice, dependency or security-setting
change; no installation or live profile. Verifier/full vendor inputs match the
prior actual PowerShell 7.6.9 exit-0 gate for 263 files; no new runtime execution.
The separate historical wrapper assertion failure remains retained.

These are headless Chromium workflow observations at one viewport, not desktop,
mobile hardware, general keyboard accessibility or native dialog acceptance.
No dialog, native focus destination/reentry or exhausted Tab-wrapping probe is
added. The local loopback EACCES and native-window denials remain untouched.
