# Spam Calls

An original, offline synthetic opt-out planner and evidence tracker. The first prototype uses invented cases and fictional brokers to demonstrate a manual workflow. It makes no removal or spam-reduction claims.

With Node.js 22 or newer installed, run `npm start`, then open `http://127.0.0.1:4173`. Run `npm test` for behavior checks. There is nothing to install: the app has no third-party runtime or test dependencies. The server binds only to loopback and serves five allowlisted app files. Internet access is unnecessary.

Choose a demo case and broker, select the matching demo identity, choose a simulated event and its synthetic evidence, then explicitly approve that step. Record submission, pending confirmation, and confirmation in order. The timeline retains the event trail; corrections append an explanation and reopen the item as unresolved. The identity check is a demo context check, not real authentication.

History stays in this browser's localStorage for the fixed loopback origin. Use Preview export before downloading synthetic JSON; import validates and previews before applying. Reset asks for confirmation. Use a current browser supporting Web Locks to serialize writes across tabs. A changed store requires reloading; storage failures never silently replace history. Browser storage can still be cleared by the browser or device, so export if you want to retain a demo.

- [Implementation plan](docs/plan.md)
- [Prototype acceptance specification](docs/prototype-spec.md)
- [Domain vocabulary](GLOSSARY.md)
- [Skill sources and compatibility](docs/skills.md)
- [Foundation review](docs/foundation-review.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

Development guidance includes the complete pinned Matt Pocock and P-Stack **skill text** collections, accessed through two project-local routers under `.agents/skills/`. Upstream executables and installers are excluded. No recurring jobs, connected mailboxes, broker searches, or submission services are configured.

The inspiration reference is [Spam-Call Scrubber by Arash](https://x.ai/bot/fUj6TYhiW_cjtzWvbsFgz), viewed on 2026-10-19. This project is independent; it does not copy that bot's implementation or activate it.

Original project work is licensed under [MIT](LICENSE), as approved by the owner on 2026-10-19. Included third-party text retains its separate MIT notices and attribution.
