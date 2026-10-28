# Cloud storage UI smoke checks

## Assignment and baseline

On 2026-10-28, the cloud checkout was clean at
`c3913bfe423aede57a9dd0b5a6bdc8fe342b0861`. The existing ready task in
`prototype-review.md`, “Next concrete milestone”, asks for repeatable browser
checks including error recovery, reset confirmation, and unavailable-storage UI.
This change covers that storage subset without changing the application.

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

Three browser checks passed on 2026-10-28:

- Corrupt synthetic JSON disables recording/import/export. Cancelling reset
  preserves the corrupt bytes; explicitly confirming reset restores an empty
  export and permits a new synthetic event.
- A denied `localStorage` getter reports the error and disables controls.
  Confirming reset reports its failure without claiming recovery.
- A quota failure after one successful event clears one-use approval, leaves
  the exported history unchanged, and retains the same history after reload.
  Retrying then appends the next valid event while retaining the original.

The unchanged Node suite also passed: 14 tests, 0 failures. Initial smoke
assertions against the disabled fieldset were rejected by Playwright despite
its disabled child controls. Assertions now check the actual user controls.
That was a harness correction, not an application defect or a claimed TDD
red/green product fix.

## Acceptance limits

No interactive cloud browser tool is exposed in this session. Installed
Chromium/Playwright can test DOM-visible behavior and synthetic storage failure
handling. This selected run does not repeat earlier dialog actions, Escape,
layout, or focus tests, and makes no modal background-inaccessibility claim.
Native browser-window focus destination, browser chrome focus, and reentry
remain unverified here. Headless output cannot close those requirements.
The previously denied native-window binding/capture action was not retried or
bypassed; no local dispatch or private-file transfer occurred.

The workflow uses the installed Matt Pocock behavior-testing guidance at the
already specified browser UI seam and independent spec/standards review, plus
P-Stack `principle-prove-it-works` and `principle-boundary-discipline`. No tracker
configuration, application dependency, live data, account/service setup,
credential, permission, publication, or deployment change is part of this task.
