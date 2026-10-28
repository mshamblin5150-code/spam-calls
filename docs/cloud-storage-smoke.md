# Cloud storage and import UI smoke checks

## Assignment and baseline

On 2026-10-28, the cloud checkout was clean at
`c3913bfe423aede57a9dd0b5a6bdc8fe342b0861`. The existing ready task in
`prototype-review.md`, “Next concrete milestone”, asks for repeatable browser
checks including error recovery, reset confirmation, and unavailable-storage UI.
This change covers the storage and preview/apply import subset without changing
the application. The initial storage commits are `3a18c23` and `39d795b`;
the continuation adds the already requested repeatable import checks.

The coordinator supplied later evidence that dialog actions, Escape, focus
restoration, and narrow layout had passed. It also relayed owner approval of the
native-dialog criterion: background application controls must be inaccessible
while modal, with correct actions and restoration; browser chrome focus may
occur. Strict uninterrupted Tab wrapping is not required. Those later local
notes are absent from this checkout. This document preserves that distinction
and does not replace or certify the missing native acceptance record.

## Run

From the repository root, on a Linux cloud runner with Node 22+, Python 3,
the Python `playwright` package, and a `chromium` or `google-chrome` executable
already available:

```sh
python test/browser_storage_smoke.py
npm test
```

The script installs nothing. Python Playwright is an optional smoke-test
dependency, separate from the dependency-free application and Node suite.
Missing prerequisites fail the opt-in check rather than silently skipping it.
The observed runner had Python Playwright 1.62.0, Chromium 154.0.8037.57, and
Node 24.19.0. The script reports the actual browser version on each run.

Each test uses a fresh nonpersistent browser context. The runner starts the
actual allowlisted server on an OS-selected loopback port and closes its own
server, browser, and contexts afterward. It never attaches to an existing
browser/profile or reads an existing store. Requests outside its exact test
origin are aborted and fail the test. Synthetic corruption and denial are
injected only into these disposable contexts at the browser storage boundary.
No application modules are mocked.

## Observed results

Six browser checks passed on 2026-10-28 (9.509s):

- Corrupt synthetic JSON disables recording/import/export. Cancelling reset
  preserves the corrupt bytes; explicitly confirming reset restores an empty
  export and permits a new synthetic event.
- A denied `localStorage` getter reports the error and disables controls.
  Confirming reset reports its failure without claiming recovery.
- A quota failure after one successful event clears one-use approval, leaves
  the visible status, timeline, and exported history unchanged, and retains the
  same history after reload. Retrying then appends the next valid event while
  retaining the original and advances the visible status and timeline.
- Import preview's displayed JSON equals the complete merged two-event payload
  while persisted bytes, visible status, and timeline remain unchanged. Cancellation preserves the
  original export across reload. Explicit apply advances the visible history
  and persists the exact events; repeated import retains one copy across reload.
- Editing a validated preview returns the action to preview. Malformed JSON
  and an unknown state field each leave the modal open, show the validation
  error, and preserve stored bytes and the visible history. A valid import
  subsequently succeeds and survives reload.
- A quota error during apply preserves stored and visible history, reports the
  error, and returns the action to preview. Cancelling and reloading retain the
  original export; a fresh preview and apply succeed after the fault is removed.

The unchanged Node suite also passed: 14 tests, 0 failures. Initial smoke
assertions against the disabled fieldset were rejected by Playwright despite
its disabled child controls. Assertions now check the actual user controls.
That was a harness correction, not an application defect or a claimed TDD
red/green product fix.

The import fixture appends only the known `cedar-awaiting` artifact to the
submission created through the UI. It reuses that submission's timestamp,
which is a supported equal-time transition, and never reads another context's
store. Assertions on background DOM status while a modal is open inspect
rendered state only; they do not attempt interaction or establish focus behavior.

## Review history and source integrity

Separate same-family Matt Pocock spec and standards reviewers inspected the
change against `c3913bf`. Standards reported zero findings. Spec reported one
low-severity coverage gap: the failed-write check needed visible status and
timeline assertions in addition to exported history. Those assertions were
added; the spec reviewer rechecked and marked the finding resolved with no new
immediate issue. The updated browser suite passed all three checks in 4.311s.
These are bounded reviews, not an exhaustive audit.

That earlier review did not cover the final evidence-documentation additions.
The continuation requires fresh Spec and Standards reviews of the entire
immutable diff from `c3913bf`, including this document, all storage assertions,
the new import checks, and the runtime proposal. The final commit identity and
those review outcomes are delivered separately to the parent so that recording
the outcomes does not change the artifact being reviewed.

PowerShell is unavailable in this runner, so `scripts/verify-foundation.ps1`
was not executed. A Python equivalent checked all 263 preserved source files
against manifest SHA-256, Git blob hashes, byte sizes, allowed file types,
source membership, and catalog targets: all passed. Vendored sources are
unchanged. This does not waive the repository's PowerShell verification step
before any future publication; this task publishes nothing. See the
[temporary runtime proposal](powershell-runtime-proposal.md), which has not been
executed. No runtime archive or dependencies were installed or downloaded.

## Acceptance limits

No interactive cloud browser tool is exposed in this session. Installed
Chromium/Playwright can test DOM-visible behavior and synthetic storage failure
handling. Import and storage checks use dialog actions as necessary, but this
run does not repeat the dedicated Escape, layout, or focus checks and makes no
modal background-inaccessibility claim.
Native browser-window focus destination, browser chrome focus, and reentry
remain unverified here. Headless output cannot close those requirements.
The previously denied native-window binding/capture action was not retried or
bypassed; no local dispatch or private-file transfer occurred.

The workflow uses the installed Matt Pocock behavior-testing guidance at the
already specified browser UI seam and independent spec/standards review, plus
P-Stack `principle-prove-it-works` and `principle-boundary-discipline`. No tracker
configuration, application dependency, live data, account/service setup,
credential, permission, publication, or deployment change is part of this task.
