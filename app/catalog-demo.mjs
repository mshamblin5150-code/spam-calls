import { brokers } from './planner.mjs';
import { createCatalogSelection } from './catalog-selection.mjs';

// Closed, invented catalog evidence. These references attest to no real artifact.
const artifact = label => ({ label, sha256: 'a'.repeat(64), bytes: 1 });
const identity = id => `DEMO:2026:${id}`;
const observations = brokers.map((broker, index) => ({
  observationIdentity: identity(broker.id), sourceNativeId: broker.id, sourceRecordIndex: index,
  authority: 'DEMO', registryYear: 2026, activityYear: 2025,
  fieldProvenance: 'invented-demo-only',
  website: { raw: `https://${broker.domain}/`, syntax: 'https-syntax-valid', verification: 'unverified', actionable: false },
  privacyRights: { raw: '', syntax: 'unknown', verification: 'unverified', actionable: false },
}));
const fields = observations.map(observation => ({
  key: `${observation.observationIdentity}:website_raw`, sourceRecordIndex: observation.sourceRecordIndex,
  brokerId: observation.sourceNativeId, field: 'website_raw', raw: observation.website.raw,
  originalReason: 'synthetic-fixture', disposition: 'invented-reference', fieldVerification: 'unverified', actionable: false,
  candidates: [{ candidateIndex: 0, sourceSpan: [0, observation.website.raw.length],
    sourceToken: observation.website.raw, hostname: brokers[observation.sourceRecordIndex].domain,
    status: 'lexical-candidate-only', verification: 'no-network-or-ownership-validation', actionable: false }],
}));
const selected = createCatalogSelection({
  ok: true, parserVersion: 'registry-flat/2', outputSchemaVersion: 'registry-observation/1',
  artifactSha256: 'a'.repeat(64), acceptedCount: brokers.length, diagnostics: [],
  organizations: brokers.map(broker => ({ observationIdentity: identity(broker.id),
    sourceNativeId: broker.id, name: broker.label, aliasesRaw: '' })),
  observations, sourceMetadata: { source_sha256: 'a'.repeat(64),
    source_page: 'https://source.example/', source_page_updated: '2026-01-01', retrieved_on: '2026-01-02' },
}, {
  triage: { artifact: artifact('Invented lexical reference'), source: { sha256: 'a'.repeat(64) },
    method: { version: 'lexical-triage/1', networkRequests: 0, originalFieldsUnchanged: true, rule: 'Invented fixtures only' }, fields },
  research: brokers.map((broker, index) => ({
    artifact: artifact(`${broker.label}: invented report`), attribution: 'Synthetic demo fixture',
    ...(broker.id === 'cedar' ? { reportedAt: null, timing: {
      observedDate: '2026-01-01', completedDate: '2026-01-02', completedMinuteUTC: '09:30',
    } } : {}),
    findings: [{ fieldKey: fields[index].key, candidateIndex: 0,
      sourceSpan: fields[index].candidates[0].sourceSpan, sourceToken: fields[index].raw,
      hostname: broker.domain, outcome: 'unresolved', actionable: false }],
  })),
});

export function selectDemoCatalog(brokerId) {
  return selected.ok ? selected.catalog.select(identity(brokerId)) : { ok: false, code: 'catalog-unavailable' };
}
