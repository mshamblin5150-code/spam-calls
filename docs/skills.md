# Skill installation and provenance

## Project-local text collections

Two discoverable routers live in `.agents/skills/`: `matt-pocock` and `pstack`. Their `catalog.json` files enumerate all source skill entries, including experimental Matt Pocock entries and P-Stack's dormant Benny resources. Source paths retain their original relative layout beneath `references/upstream/`.

This is a reviewed text-only installation, not an upstream plugin installation. Only Markdown, TSV reference text, and the original LICENSE files are copied. Every copied file is checked against its pinned Git blob before installation. Each collection has a manifest with the commit, upstream path, Git blob ID, SHA-256, and byte count. `scripts/verify-foundation.ps1` checks those properties offline. Catalogs and routers are local additions, distinct from upstream source.

The source repositories were downloaded using Git without running their programs, hooks, package managers, or installers. The generic skill-installer guidance was consulted; its normal global helper installation was replaced by this project-scoped text copy to meet the requested installation boundary.

## Source identity

- Matt Pocock: `mattpocock/skills`, commit `49dd158d1076134a641b33efb035946536778336`, advertised plugin version 1.3.1. The official AIHero setup article links this repository: https://www.aihero.dev/skills-setup-matt-pocock-skills. All source `SKILL.md` entries are retained, including entries outside the 27 registered engineering/productivity skills.
- P-Stack: `cursor/plugins`, `pstack/`, commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`, version 0.15.9. This is the exact commit pinned by the installed P-Stack collection's source guidance. All 50 main skills and the dormant Benny skill text are retained.

## Review findings and compatibility

Upstream text includes shell commands, dependency installation suggestions, browser/credential setup, model-specific delegation, merge workflows, transcript lookup, and recurring automation instructions. These are reference instructions, not actions performed by installation. P-Stack's Bun bootstrap and other executable helpers are excluded. Some referenced scripts, images, YAML agent metadata, and plugin manifests therefore will not resolve locally. A dependent workflow must report the missing resource instead of inventing or downloading a substitute.

Use only the selected workflow relevant to the current task. Preserve user scope and host rules. Cursor model names, `Task`, `/loop`, sticky modes, rules files, Grok Bots, and external services are not supplied by this installation. Use a supported equivalent only with the same evidence and authorization; otherwise report the blocked step. Installation grants no permission to search personal data, access mail, collect credentials, send messages, merge, deploy, change unrelated workspaces, or establish recurring actions.

The setup-matt-pocock-skills text was read as a configuration reference. Its interactive setup flow has not been claimed complete: tracker choice and triage labels remain proposals in `plan.md`. The foundation's AGENTS.md and domain vocabulary implement the separately authorized project foundation.

Routers are available to the next agent turn when project skill discovery refreshes. Current agents can read them directly.
