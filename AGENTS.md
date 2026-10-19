# Spam Calls project instructions

Work only in this repository. Keep this project separate from DAVID and other workspaces.

The current product scope is the offline synthetic planner described in `docs/plan.md`. Use invented data and reserved example domains. Live personal-data searches, opt-out submissions, email access, credentials, and recurring actions are outside this milestone. Never commit personal cases, mailbox exports, real evidence, or secrets.

## Agent skills

For engineering work, consult `.agents/skills/matt-pocock/SKILL.md` and select the relevant authentic source using its catalog. For P-Stack guidance, consult `.agents/skills/pstack/SKILL.md`. These routers preserve upstream text and describe host compatibility; they do not activate every workflow or grant authority for external actions. Read selected workflows fully before applying them.

The canonical domain vocabulary is `GLOSSARY.md`; architectural decisions belong in `docs/adr/` when an implementation decision is made. Issue-tracker configuration and triage labels are proposed in `docs/plan.md`, pending a later workflow choice. Skill installation is complete independently of that optional configuration.

Before publishing, inspect the complete staged file list and diff for secrets, personal data, unrelated content, third-party notices, and unintended executables. Run `scripts/verify-foundation.ps1` to verify vendored hashes. Preserve upstream bytes and notices; record any future source update with a new commit pin and manifest.
