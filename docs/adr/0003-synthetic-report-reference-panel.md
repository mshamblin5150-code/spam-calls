# Synthetic report reference panel

Status: proposed bounded demo UI integration.

Show the selected broker fixture's report timing in a read-only definition list
below the evidence timeline. Keep simulated event history separate from report
provenance so a saved event never supplies a missing report timestamp.

`app/catalog-demo.mjs` supplies closed, invented snapshot and reference objects
to `createCatalogSelection`. It uses the existing broker fixtures and reserved
example domains. Its artifact identifiers are explicit synthetic placeholders,
not hashes of real evidence. It imports no adapter and performs no acquisition.

The Cedar fixture has an unknown report time and known observation and
completion dates with a completion minute. The Harbor fixture omits all timing.
The panel labels unknown values as `Unknown` and shows completion minutes with
their UTC zone and precision. It preserves each known date as supplied.

Render every value with `textContent`. The panel adds no links, forms, storage
records, export fields, or destination actions. The server allowlist adds only
the consumer and closed-fixture modules needed by the UI. Existing CSP and
network restrictions remain unchanged.

Browser checks select both broker fixtures and verify visible timing, absence
of links, no new persisted history, and no non-test-origin requests. These
checks establish the synthetic UI only. Real-data integration, personal vault
behavior, destination approval, and native acceptance remain separate work.
