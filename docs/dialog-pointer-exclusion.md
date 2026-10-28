# Bounded modal pointer-exclusion evidence

## Scope

This separate acceptance slice starts from merged main
`af2568683ed1260084f34ed5014fda56dc5a40fe` on local branch
`cloud/dialog-pointer-exclusion`. The completed storage/import/verifier
milestone and its historical logs remain intact. This change adds tests and
evidence only; it changes no application, verifier, vendor, manifest, notice,
dependency, or installation configuration.

Exact limited claim: in fresh nonpersistent headless Chromium contexts, real
browser mouse clicks at the specified background-control coordinates do not
activate those controls or change their associated state while export, initial
import, or reset is an active native HTML modal. The same controls receive
trusted input and perform their actions after cancellation.

This is tested pointer interaction only. It establishes neither keyboard
exclusion, accessibility-tree behavior, native-window focus destination/reentry,
other browsers/viewports, every background control, every later import state,
nor full native-dialog acceptance. Strict uninterrupted Tab wrapping is not
required by the owner's revised criterion; no Tab, Escape, activeElement,
browser-chrome, or native-window focus probe is added here. No denied native
capture/binding route or local Alienware action is involved.

## Repeatable check

Prerequisites remain the existing optional smoke-test tools: Node 22+, Python
Playwright, and an already available Chromium executable. Nothing is installed.
The existing harness serves the real app on an OS-selected loopback port,
blocks unexpected external requests, records unhandled page errors, and closes
its server, browser, and fresh per-test contexts.

Focused invocation from the repository root:

```sh
python test/browser_storage_smoke.py \
  StorageUI.test_export_modal_excludes_tested_background_pointer_input \
  StorageUI.test_import_modal_excludes_tested_background_pointer_input \
  StorageUI.test_reset_modal_excludes_tested_background_pointer_input
```

Full browser suite: `python test/browser_storage_smoke.py`.
Default domain/storage/server suite: `npm test`.

Each modal scenario uses a fresh context and a 2000×1600 CSS viewport so the
four target centers lie outside the foreground dialog rectangle and inside
the viewport. All targets must be visible and enabled. A synthetic submission
is recorded through the UI, then a valid issue command is prepared so a leaked
submit would have a real observable persistence effect.

| Background target | Required post-cancel liveness |
| --- | --- |
| `#export` | Opens the synthetic export modal |
| `#brokers .broker:nth-child(2)` | Changes Cedar Directory to Harbor Index |
| `#approval` | Toggles off and back on |
| `#event-form button[type=submit]` | Saves the prepared synthetic issue, retaining the original submission |

After opening each modal normally, the test verifies `:modal` and its identity.
It then uses `page.mouse.click(x, y)` at each recorded target center. Capture
listeners only record events and are explicitly passive. Every probe must
produce trusted `pointerdown` and `click` events, with the recorded events
targeting the active dialog rather than any of the four background controls.
The case, broker, identity, event, artifact, approval, visible status/timeline,
stored history bytes, and modal set must remain unchanged.

Cancellation uses the dialog's actual button with browser mouse input. The
test then clicks the same recorded background coordinates, requiring trusted
events at each intended control plus the visible/persisted effects above.
This prevents a nonfunctional control, missed input, or empty fixture from
making the exclusion assertion pass vacuously.

Pointer probes, cancellation, and post-cancel liveness use no forced clicks,
JavaScript activation calls, synthetic event dispatches, or timeout-only
blocking assertions. Before the modal opens, the existing UI helpers select
fixture options and prepare the valid command. JavaScript evaluation is
limited to state inspection and event-observer bookkeeping. This checks the
pointer aspect of modal inertness using actual browser input, rather than
inferring it from an `inert` attribute or actionability timeout.
[HTML inert subtrees](https://html.spec.whatwg.org/multipage/interaction.html#inert-subtrees),
[Playwright mouse input](https://playwright.dev/python/docs/api/class-mouse),
[Playwright actionability](https://playwright.dev/python/docs/actionability).

## Observed outcome and limits

The initial focused run passed all three tests in 6.298s on headless Chromium
154.0.8037.57. That covered 12 blocked background-target probes across the
three modal scenarios and successful post-cancel liveness for all four targets
in each scenario. It did not demonstrate a product defect or require a product
fix. This is behavior coverage of an already implemented browser boundary,
not a claimed test-first product red/green fix.

The full browser suite subsequently passed all nine tests in 14.370s, including
the six previously merged storage/import checks and these three pointer checks.
The unchanged Node suite also passed: 14 tests, 0 failures. No PowerShell runtime
was downloaded or executed for this slice; verifier inputs are unchanged.

Installed Matt Pocock behavior-testing guidance is applied at the explicitly
approved browser UI seam. P-Stack `principle-prove-it-works` governs event/state
evidence and its limits. Independent Spec and Standards review will inspect the
final immutable diff; the exact commit and outcomes are reported separately so
the reviewed artifact is not changed afterward to record its own review.

The combined-suite result is reported with the final handoff. No publication,
merge, deployment, installation, or full native-dialog acceptance closure is
part of this local test/evidence task. The existing native focus and broader
background-inaccessibility limitations remain open outside the tested slice.
