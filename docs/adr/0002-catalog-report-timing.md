# Catalog report timing

Status: accepted consumer contract; the demo uses closed synthetic references.

`app/catalog-selection.mjs` selects an organization and its caller-supplied
evidence references from a registry-observation snapshot. It performs no
acquisition, persistence, or destination activation. The demo UI loads it through
`app/catalog-demo.mjs`, which supplies invented references for the two broker fixtures.

A historical report may state an observation date or completion minute without
establishing an exact report timestamp. Requiring an exact `reportedAt` would
reject that evidence or encourage callers to invent precision.

Preserve absent and null `reportedAt` values as supplied. When a caller supplies
an exact timestamp, retain the canonical ISO validation. Optional `timing`
metadata contains only `observedDate`, `completedDate`, and
`completedMinuteUTC`. Dates must be actual `YYYY-MM-DD` calendar dates. A
completion minute must use `HH:mm` in UTC and have its own completion date.
Date-only evidence is valid. A present timing object must contain at least one
known value; empty objects, null values, and unknown keys are rejected.

Observation, completion, and report time describe distinct events. Preserve
independently supplied facts without filling missing fields, adding seconds,
forcing equality, or deriving freshness. For example, an invented report can
retain this metadata:

```json
{
  "reportedAt": null,
  "timing": {
    "observedDate": "2026-01-01",
    "completedDate": "2026-01-02",
    "completedMinuteUTC": "09:30"
  }
}
```

Artifact metadata and attribution remain caller attestations. Selection checks
their shape and binds each finding to its exact field, candidate index, source
span, raw token, and hostname. It does not authenticate report bytes or prove
that a claimed time is true. Links remain non-actionable, activation remains
held, and destination approval remains absent. This module adds no authority
for personal-data workflows or external actions.

Synthetic tests exercise `createCatalogSelection` and the selected evidence
references. They cover legacy exact timestamps, unknown timing, date-only and
minute precision, malformed input, and retained occurrence checks. They do not
establish native acceptance or live integration. The optional browser checks
separately verify the synthetic panel and unchanged storage behavior.
