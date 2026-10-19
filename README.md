# Spam Calls

An original, offline synthetic opt-out planner and evidence tracker. This repository currently contains the reviewed project foundation and implementation plan; an application has not been built yet.

The planned first version uses invented cases to help someone understand a manual opt-out workflow: plan a task, record a simulated action, attach synthetic evidence, and review what remains unresolved. It makes no removal or spam-reduction claims.

- [Implementation plan](docs/plan.md)
- [Domain vocabulary](GLOSSARY.md)
- [Skill sources and compatibility](docs/skills.md)
- [Foundation review](docs/foundation-review.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

Development guidance includes the complete pinned Matt Pocock and P-Stack **skill text** collections, accessed through two project-local routers under `.agents/skills/`. Upstream executables and installers are excluded. No recurring jobs, connected mailboxes, broker searches, or submission services are configured.

The inspiration reference is [Spam-Call Scrubber by Arash](https://x.ai/bot/fUj6TYhiW_cjtzWvbsFgz), viewed on 2026-10-19. This project is independent; it does not copy that bot's implementation or activate it.

The license for original project work is undecided. Public visibility does not grant a license to original work. Included third-party text remains under its respective MIT license.
