# Static synthetic prototype

Status: accepted for this bounded milestone, 2026-10-19.

Use native HTML/CSS and ES modules, with Node's built-in test runner and a loopback-only allowlisted file server. The workflow is a small form and append-only timeline, so framework and package-manager dependencies would add no necessary capability. The domain is pure; persistence and browser presentation are separate modules.

Cases, brokers, observations, and evidence artifacts come from a closed fixture registry. This intentionally sacrifices custom note/attachment entry to keep the prototype synthetic-only. Imports accept only this schema and registry. The identity/approval fields are explicit demo attestations; they do not establish real identity or authorization.

Writes use a named browser Web Lock and a persisted-baseline comparison. Web Locks serialize cooperating demo tabs; the baseline check rejects stale views. The synchronous storage adapter alone is not a general compare-and-swap database. All writes in the browser UI, including reset/import, go through that lock. Unsupported browsers fail saving visibly.

The generated concept uses white, navy, teal, a pale gray case rail, native forms, and an evidence timeline. Functional changes from the concept are deliberate: the event/evidence fields precede approval so the operator approves the chosen action; a demo-authentication clarification, fixture-only notice, explicit item status, and error messages communicate the actual contract. Narrow screens stack the rail above the detail panel. No generated imagery is shipped as UI.
