# Spam Calls project instructions

Work only in this repository. Keep this project separate from DAVID and other workspaces.

The current product scope is the offline synthetic planner described in `docs/plan.md`. Use invented data and reserved example domains. Live personal-data searches, opt-out submissions, email access, credentials, and recurring actions are outside this milestone. Never commit personal cases, mailbox exports, real evidence, or secrets.

## Agent skills

For engineering work, consult `.agents/skills/matt-pocock/SKILL.md` and select the relevant authentic source using its catalog. For P-Stack guidance, consult `.agents/skills/pstack/SKILL.md`. These routers preserve upstream text and describe host compatibility; they do not activate every workflow or grant authority for external actions. Read selected workflows fully before applying them.

The canonical domain vocabulary is `GLOSSARY.md`; architectural decisions belong in `docs/adr/` when an implementation decision is made. Issue-tracker configuration and triage labels are proposed in `docs/plan.md`, pending a later workflow choice. Skill installation is complete independently of that optional configuration.

Before publishing, inspect the complete staged file list and diff for secrets, personal data, unrelated content, third-party notices, and unintended executables. Run `scripts/verify-foundation.ps1` to verify vendored hashes. Preserve upstream bytes and notices; record any future source update with a new commit pin and manifest.

## Harness consistency checkpoints

Use these checkpoints in the existing slice brief, review and closeout; do not create a parallel tracker. Keep this repository's scope, glossary, ADRs, approvals and security requirements authoritative. Canonical Assimilation guide: [Harness Engineering](https://github.com/mshamblin5150-code/assimilation/blob/main/docs/HARNESS_ENGINEERING.md).

1. **Before a slice:** name the actual requirement and its source, the observable done state at the public seam, and the smallest relevant verification. Identify the current owner, allowed writes and any existing holds. For changed behavior, use the installed Pocock TDD guidance at the agreed seam; report coverage of existing behavior as initially green when it is. Do not manufacture a red.
2. **During existing review:** keep Pocock's spec and standards findings distinct. For every proposed blocking gate, cite the requirement or documented project rule it checks; label uncited suggestions as suggestions. Challenge harness work that adds no evidence for the slice. Expand a harness only to close a named observation gap, explaining what the added check proves, misses and costs. Existing privacy, security, native-acceptance and publication requirements remain binding.
3. **At closeout:** record the artifact/revision, exact verification and observed result, evidence location, limitations, outstanding holds and the next concrete slice with owner. Distinguish execution admitted, completed, tested and source-reviewed. Classify tooling/access failure separately from product failure; uncertain execution stays uncertain until observed. A passing synthetic test proves only its scoped behavior.

Use the installed P-Stack boundary-discipline, test-behavior-not-implementation, sequence-verifiable-units and prove-it-works guidance alongside these checkpoints. A documentation-only instruction change needs source/diff review, not an application, browser or server run. Preserve required pre-publication checks in this file. Do not install helpers or configure proposed trackers merely to apply these checkpoints.

Carry current holds forward explicitly in the existing private handoff: URL triage does not authorize disclosure; no real-data, transport, native or live integration is implied. Preserve recorded predecessor terminal states, server liveness/custody uncertainties, unknown admissions and native/integration/publication/merge holds until separately resolved by authorized observed evidence. Do not adopt, restart or stop an uncertain session to verify a documentation slice.
