# Prototype verification and review, 2026-10-19

## Delivered behavior

The dependency-free static prototype implements two synthetic cases and two fictional brokers, matching demo identity checks, one-use action approval, fixture-backed ordered status transitions, append-only corrections, local persistence, validated import preview/application, export preview/download, and confirmed reset. Follow-up dates are fixed fixture labels marked display-only. Original work is MIT under the owner's explicit approval; upstream notices and source bytes are unchanged.

Run `npm start` with Node 22+ and open `http://127.0.0.1:4173`. Run `npm test` for the automated suite. No install step is required. The server exposes only the five app routes and binds to loopback.

## Tests and observed failure cases

Final `node --test test/*.test.mjs`: **14 passed, 0 failed**. The HTTP integration test required local-loopback permission because the sandbox's client socket failed with EACCES. With that permission, the complete suite passed. No Internet or broker requests are involved in the test.

The tests cover identity mismatch, absent/non-boolean approval, wrong broker/evidence, skipped transitions, unknown event types/cases/fields, invalid timestamps, full confirmation and correction trails, public status validation, duplicate/reordered/conflicting imports, malformed/unsupported/oversized payloads, reload persistence, isolated snapshots, preview without mutation, write failures, corrupt/unavailable storage, deliberate reset recovery, stale writes, HTTP allowlisting, rejected POSTs, and CSP network restrictions.

The initial domain and persistence tests were run before their respective modules existed and failed, then passed after implementation. Both review regressions were separately observed failing before their fixes, then passing. This follows the installed TDD/behavior-testing guidance at the explicitly requested workflow, import/export, and persistence boundaries. It is not a claim that every individual test was written through a separate red/green cycle.

## Independent two-axis review

Matt Pocock's installed code-review workflow was applied with independent same-family spec and standards agents. Baseline: `d7fc223e957209cf98ac8a5ccf6a35a96d13a98e`; initial prototype: `b9f058839f1e4d7e875b41505bc19a559463237c`. The spec was the local `prototype-spec.md` plus `plan.md`; the review did not require issue-tracker writes.

**Spec:** one low-severity finding: displayed follow-up dates required by the plan were missing. Fixed with deterministic fixture dates in the checklist, explicitly display-only. Reviewer recheck: resolved, no immediate regression, 13 domain/storage tests passed.

**Standards:** two findings: public `statusFor` trusted raw events; identical imported event fields in a different JSON property order were considered conflicting. Fixed with public boundary validation/private validated lookup, and field-value comparison independent of property order. Two new regression tests failed before the fixes and passed afterward. Reviewer recheck: both resolved, seven domain tests passed, no new immediate findings.

Final outstanding findings: **Spec 0; Standards 0** in these bounded passes. This is not an exhaustive security audit.

## Browser evidence and visual checks

Chrome Browser Use loaded the app after the local server was restarted with loopback access. At 1536×1024 with network emulation offline, the UI rejected a mismatched identity with no event, then completed submission -> pending confirmation -> simulated confirmation. Each successful step cleared identity/approval. Export preview displayed the three validated events and the explicit download action completed. Malformed import displayed an error without losing confirmed status. Reimport preview showed exactly three events, and applying it retained one copy. Cancelling reset preserved history. A correction appended its superseded event ID and yielded unresolved; reloading retained all four events and the original trail.

At 390×844, the rail stacked above the detail panel, toolbar controls wrapped, and the measured document width was 375px with no horizontal overflow. Switching to Demo Case B showed its empty history and unchecked approval. Native controls and visible focus styles support keyboard use; keyboard navigation was used during screenshot checks. Browser reset cancellation was exercised; approved reset/recovery is covered by the storage tests, not a claimed browser click-through.

The generated visual concept and actual desktop/mobile captures were inspected using `view_image`. Local QA files are under ignored `local-data/qa/`; none are published. Concept: `concept.png`; desktop captures: `desktop.jpg` and `desktop-confirmed.png` (the browser returns JPEG bytes for screenshot capture); mobile: `mobile.jpg`. The concept prompt requested the complete primary synthetic planning screen, white/navy/teal palette, pale case rail, native forms, explicit identity/approval/evidence controls, timeline, local data controls, and no imagery or external actions. Built-in Image Gen supplied the concept; no image-generation API credentials were used.

Comparison checked six concrete points: white background and teal action color; navy/system typography hierarchy; rail/detail layout; native form geometry; divider/timeline treatment; and narrow-screen wrapping. The implementation follows the concept's layout and palette with the functional changes recorded in ADR 0001: approval follows the selected event/evidence, clarifying notices and explicit status are added, broker status/date rows stack for readability. No raster mockup is shipped as UI. The comparison is to this adapted functional design, not a claim of pixel-identical reproduction.

## Browser permission and export-file checkpoint

The long browser-tool call used CDP `Network.enable`, `Network.emulateNetworkConditions`, and `Emulation.setDeviceMetricsOverride` for scoped QA. It eventually returned; subsequent UI checks succeeded. These were platform tool permissions, not repeated conversational approval requests. There is no evidence that the platform persisted the user's “Always allow” selection.

Offline emulation was restored to normal before the successful persistence reload. After the mobile check, the runtime lost its bindings and reconnecting to the prototype tab failed with `Debugger unattached`. No action was pending at that failure, and no enforced permission was bypassed. The temporary 390px viewport cleanup could not be confirmed. Further browser calls stopped. Reconnecting/allowing the browser debug session through its UI would be necessary only for additional browser checks or viewport cleanup; it does not block the completed code/test milestone.

The expected saved file was `spam-calls-synthetic-demo.json`, generated by the app's explicit download. It was found in the project root, moved to ignored `local-data/qa/synthetic-export.json`, and validated through the public import boundary: schema 1, demo-v1, three events (submission, awaiting, confirmation), with closed-registry identities/artifacts and no extra fields. It contains no credentials, browser configuration, arbitrary personal fields, or unrelated private state. It is excluded from Git. Saving it does not grant browser debug-tool permissions.

## Provenance and limits

Actual installed source guidance read: Matt Pocock `implement`, `implement-spec` (assessed, not used as a ticket-graph orchestrator), `tdd` with tests/mocking references, and `code-review`; P-Stack `principle-boundary-discipline` and `principle-test-behavior-not-implementation`, building on the foundation's `principle-foundational-thinking` and `principle-prove-it-works` reads. The project routers and original `writing-for-agents` guidance govern the documentation. Host frontend-app-builder, imagegen, computer-use and browser runtime guidance supported UI concepting/QA. Upstream executable helpers were not run. All 263 vendored files remain checked by the foundation verifier against their pinned manifests.

The three Benny skill texts are unchanged dormant contents of pinned P-Stack's `automations/benny/skills/`, retained with the rest of that collection's text to preserve reference completeness. They are not separate active automations, not invoked by this prototype, and their external integrations/scripts/configuration are absent. Source pins and licenses are documented in `skills.md` and `THIRD_PARTY_NOTICES.md`.

This is a synthetic demo, not authentication, a legal authority system, or a real removal service. LocalStorage can be edited or cleared by the browser/user; validation enforces the demo schema, not cryptographic authenticity. Cross-tab locking coordinates cooperating app tabs, not arbitrary other software. Imports are deliberately limited to this demo fixture set. No real personal-data search, broker adapter, submission, mailbox, credential collection, telemetry, external asset dependency, service worker, or schedule was added. DAVID and other projects were untouched.

## Next concrete milestone

Stay offline and synthetic: add repeatable browser smoke tests for approval clearing, error recovery, preview/apply import, reset confirmation, and 390px keyboard operation. Keep the same closed fixtures and validate both supported browser storage and unavailable-storage UI paths. Do not introduce live broker integrations as part of that next step.
