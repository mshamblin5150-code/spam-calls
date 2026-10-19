# Offline synthetic planner: implementation plan

## Intended experience

Open a local application, choose an invented demo case, see a checklist for a fictional broker, record a simulated step, and inspect an evidence timeline. Close and reopen the application without losing that local history. Export only a synthetic case with an explicit preview. The product must work with networking disabled.

The reference bot advertises broker discovery, opt-out submission, email confirmation, and scheduled rechecks. Those capabilities are inspiration only. This original milestone implements planning and evidence organization using invented fixtures.

## Domain and behavior

Use separate structures for cases, broker fixtures, plan items, and evidence events. Each persisted record carries a schema version and stable local identifier. Broker fixtures use `.example` domains and describe simulated steps in their own words. Cases use labels such as `Demo Case A`, without phone numbers or addresses.

A plan item starts as `planned`. Recorded events can move its displayed status to `simulated-submission`, `awaiting-simulated-confirmation`, `simulated-confirmed`, or `unresolved`. Events retain their timestamp, event type, observation, and synthetic artifact reference. Corrections append a superseding event rather than silently rewriting evidence. Unsupported transitions fail at the input boundary. A note or a click alone never becomes proof of removal.

Follow-up dates appear in the checklist. They do not create background processes, notifications, scheduled tasks, or network requests.

## Delivery sequence and acceptance

1. **Domain slice:** implement pure planning and event-reduction functions with literal expected outcomes for valid transitions, rejected transitions, duplicate imports, and corrections. Done when an invented case progresses through the workflow and retains its complete event history.
2. **Local experience:** choose the smallest appropriate UI stack, then build a case picker, checklist, item detail, and evidence timeline. Done when the full demo workflow works with the network disabled and every status is visibly labeled as simulated.
3. **Persistence:** introduce a versioned local store and explicit reset/export controls. Done when reload preserves events, malformed imports leave the existing store intact, repeated imports do not duplicate events, and reset requires a deliberate action.
4. **Review and portability:** preview a synthetic export, reopen it in a fresh local store, and confirm equivalent history. Test keyboard use, empty states, long notes, storage failure, and narrow screens. Done when exports contain only fixture content and no application route makes external requests.

The foundation deliberately adds no runtime dependencies or framework. Choose the stack when implementing the first user-visible slice, with local operation and a small dependency surface as constraints.

## Future decisions

- Original-code license: owner decision remains open.
- Proposed tracker: this repository's GitHub Issues, with PRs as a request surface off. Proposed triage labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. These have not been configured or treated as an accepted workflow.
- Matt Pocock's setup workflow requires presenting a concrete tracker/configuration draft for user choice. Installing its source does not execute that configuration flow.
- Any real-data or external-action capability requires a separately scoped request and design review. It is not part of this implementation plan.
