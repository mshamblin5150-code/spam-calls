# Offline prototype specification

This implements the first local workflow from `plan.md` with no external dependencies. It is a static HTML/CSS/JavaScript application served only on loopback. The owner approved MIT for original work on 2026-10-19; upstream notices retain their separate attribution. Publish only after the synthetic milestone's tests and review pass.

## Acceptance boundaries

- Two fixed invented case labels, two fictional brokers using `.example`, and a closed registry of synthetic artifacts. There are no free-text identity/contact/evidence fields or file attachments. Unknown records and extra import fields are rejected.
- For every recorded event the operator selects the matching demo case identity and explicitly approves that exact case, broker, and event. This is a synthetic context check and self-attestation, not real authentication or legal authority. Approval is one use; changing context clears it.
- Status is derived solely from validated append-only events. `planned` -> `simulated-submission` -> `awaiting-simulated-confirmation` -> `simulated-confirmed` requires the corresponding fixture artifact at every step. An issue event yields `unresolved`; a new simulated submission may restart that workflow. No state means real removal.
- A correction references the last event for that plan item, appends a fixture explanation, and yields `unresolved`. The original event stays visible. No deletion or silent history edits.
- Schema-versioned events contain stable IDs, ISO timestamps, case/broker IDs, verified demo identity, explicit approval, event type, and a known artifact. Imports are size-limited and validated in full before any local mutation. Repeated imports do not duplicate events; ID collisions, unsupported schemas, invalid order, forged statuses, and unknown content fail atomically.
- Persistence uses browser localStorage on the fixed loopback origin. Corrupt or unavailable storage is shown as an error; existing data is not silently overwritten. Failed writes leave visible and stored state unchanged. Stale writers fail instead of losing another tab's events. Explicit reset is confirmed and can recover corrupt demo storage.
- Export is a preview of the validated synthetic JSON, followed by an explicit download action. Imported data is previewed, then explicitly applied. Reset has a confirmation step. There are no follow-up timers, subscriptions, network APIs, broker links, forms posting data, mailbox operations, credentials, analytics, external fonts, or service workers.

## Test seams

The authorized behavior tests exercise the public workflow API, validated import/export, and persistence adapter. They observe the resulting status and event history, rejected commands, atomic failures, reloads, and stale writers. Browser checks cover the complete form workflow, approval reset, timeline, export/import preview, reload, empty states, and narrow layout. Node's built-in runner is sufficient; no package installation is needed.

## Review baseline

Compare the prototype branch to foundation commit `d7fc223e957209cf98ac8a5ccf6a35a96d13a98e`. Spec review uses this document plus `plan.md` and the delegated scope. Standards review uses root AGENTS.md, GLOSSARY.md, this boundary design, and the installed Matt Pocock code-review smell baseline. No issue tracker action is needed for this locally authorized milestone.
