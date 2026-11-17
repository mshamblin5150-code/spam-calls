import test from 'node:test';
import assert from 'node:assert/strict';
import { createCatalogSelection } from '../app/catalog-selection.mjs';

// Invented records and caller-attested artifact references only; no adapter or retained data.
function fixture() {
  const identity = 'CPPA:2026:synthetic-1';
  const websiteRaw = 'http://fixture.example; http://shared.example';
  const rightsRaw = 'http://shared.example';
  const link = raw => ({ raw, syntax: 'unsupported-scheme', verification: 'unverified', actionable: false });
  const candidate = (candidateIndex, sourceSpan, sourceToken, hostname) => ({
    candidateIndex, sourceSpan, sourceToken, hostname, status: 'lexical-candidate-only',
    verification: 'no-network-or-ownership-validation', actionable: false,
  });
  const fields = [
    { key: `${identity}:website_raw`, sourceRecordIndex: 0, brokerId: 'synthetic-1',
      field: 'website_raw', raw: websiteRaw, originalReason: 'unsupported-scheme',
      disposition: 'synthetic-review', fieldVerification: 'unverified', actionable: false,
      candidates: [candidate(0, [0, 22], 'http://fixture.example', 'fixture.example'),
        candidate(1, [24, 45], 'http://shared.example', 'shared.example')] },
    { key: `${identity}:privacy_rights_url_raw`, sourceRecordIndex: 0, brokerId: 'synthetic-1',
      field: 'privacy_rights_url_raw', raw: rightsRaw, originalReason: 'unsupported-scheme',
      disposition: 'synthetic-review', fieldVerification: 'unverified', actionable: false,
      candidates: [candidate(0, [0, 21], 'http://shared.example', 'shared.example')] },
  ];
  const report = {
    artifact: { label: 'Invented report reference', sha256: 'd'.repeat(64), bytes: 1 },
    reportedAt: '2026-01-02T03:04:05.000Z', attribution: 'Invented report author',
    findings: fields.map((field, index) => {
      const c = field.candidates[index === 0 ? 1 : 0];
      return { fieldKey: field.key, candidateIndex: c.candidateIndex,
        sourceSpan: [...c.sourceSpan], sourceToken: c.sourceToken, hostname: c.hostname,
        outcome: 'unresolved', actionable: false };
    }),
  };
  return { identity, report,
    snapshot: { ok: true, parserVersion: 'registry-flat/2', outputSchemaVersion: 'registry-observation/1',
      artifactSha256: 'a'.repeat(64), acceptedCount: 1, diagnostics: [],
      sourceMetadata: { source_sha256: 'b'.repeat(64), source_page: 'https://source.example/',
        source_page_updated: '2026-01-01', retrieved_on: '2026-01-02' },
      organizations: [{ observationIdentity: identity, sourceNativeId: 'synthetic-1',
        name: 'Invented Organization', aliasesRaw: '' }],
      observations: [{ observationIdentity: identity, sourceNativeId: 'synthetic-1', sourceRecordIndex: 0,
        authority: 'CPPA', registryYear: 2026, activityYear: 2025, fieldProvenance: 'registry-reported-unverified',
        website: link(websiteRaw), privacyRights: link(rightsRaw) }] },
    references: { triage: { artifact: { label: 'Invented triage', sha256: 'c'.repeat(64), bytes: 1 },
      source: { sha256: 'a'.repeat(64) }, method: { version: 'lexical-triage/1', networkRequests: 0,
        originalFieldsUnchanged: true, rule: 'Synthetic lexical fixture' }, fields }, research: [report] },
  };
}
function select(f) {
  const selection = createCatalogSelection(f.snapshot, f.references);
  assert.equal(selection.ok, true);
  return selection.catalog.select(f.identity).broker;
}

test('limited observation and completion timing survives selection without an invented instant', () => {
  const f = fixture();
  f.report.reportedAt = null;
  f.report.timing = { observedDate: '2026-11-02', completedDate: '2026-11-02', completedMinuteUTC: '19:50' };
  const broker = select(f);
  assert.deepEqual(broker.evidenceReferences.historicalResearch, [f.report]);
  assert.equal(broker.activation, 'held');
  assert.equal(broker.evidenceReferences.destinationApproval, 'none');
  assert.equal(broker.website.actionable, false);
  assert.equal(broker.privacyRights.actionable, false);
  assert.deepEqual(broker.evidenceReferences.historicalResearch[0].findings.map(x => x.candidateIndex), [1, 0]);
});

test('legacy canonical exact reportedAt survives unchanged', () => {
  const f = fixture();
  assert.deepEqual(select(f).evidenceReferences.historicalResearch, [f.report]);
});

test('absent and null exact times remain distinct without inserted timing metadata', () => {
  for (const absent of [false, true]) {
    const f = fixture();
    if (absent) delete f.report.reportedAt;
    else f.report.reportedAt = null;
    const before = structuredClone(f);
    const retained = select(f).evidenceReferences.historicalResearch[0];
    assert.deepEqual(retained, f.report);
    assert.equal(Object.hasOwn(retained, 'reportedAt'), !absent);
    assert.equal(Object.hasOwn(retained, 'timing'), false);
    assert.deepEqual(f, before);
  }
});

test('date-only evidence survives without completing an absent exact time', () => {
  for (const timing of [{ observedDate: '2024-02-29' }, { completedDate: '2026-11-02' }]) {
    const f = fixture(); delete f.report.reportedAt; f.report.timing = timing;
    assert.deepEqual(select(f).evidenceReferences.historicalResearch[0], f.report);
  }
});

test('independent exact report and observation completion times can coexist', () => {
  const f = fixture();
  f.report.timing = { observedDate: '2025-12-30', completedDate: '2026-01-01', completedMinuteUTC: '23:59' };
  assert.deepEqual(select(f).evidenceReferences.historicalResearch[0], f.report);
});

test('valid completion minute boundaries remain minute-precision strings', () => {
  for (const completedMinuteUTC of ['00:00', '23:59']) {
    const f = fixture(); f.report.reportedAt = null;
    f.report.timing = { completedDate: '2026-11-02', completedMinuteUTC };
    assert.deepEqual(select(f).evidenceReferences.historicalResearch[0], f.report);
  }
});

test('present exact times reject undefined invalid and noncanonical values', () => {
  for (const reportedAt of [undefined, '', 0, false, {}, 'not-a-date',
    '2026-01-02', '2026-01-02T03:04:05Z', '2026-01-02T04:04:05.000+01:00', '2026-02-30T03:04:05.000Z']) {
    const f = fixture(); f.report.reportedAt = reportedAt;
    assert.deepEqual(createCatalogSelection(f.snapshot, f.references), { ok: false, code: 'catalog-unavailable' });
  }
  assert.equal(select(fixture()).evidenceReferences.historicalResearch[0].reportedAt, '2026-01-02T03:04:05.000Z');
});

test('timing rejects empty null wrong-type and unknown metadata', () => {
  for (const timing of [undefined, null, {}, [], '', 1, false, { arbitrary: '2026-11-02' },
    { observedDate: null }, { observedDate: undefined }, { completedDate: 20261102 }]) {
    const f = fixture(); f.report.reportedAt = null; f.report.timing = timing;
    assert.deepEqual(createCatalogSelection(f.snapshot, f.references), { ok: false, code: 'catalog-unavailable' });
  }
  const valid = fixture(); valid.report.reportedAt = null; valid.report.timing = { observedDate: '2026-11-02' };
  assert.deepEqual(select(valid).evidenceReferences.historicalResearch[0].timing, { observedDate: '2026-11-02' });
});

test('both timing dates reject nonexistent and non-date-only calendar values', () => {
  for (const field of ['observedDate', 'completedDate']) {
    for (const value of ['2025-02-29', '2100-02-29', '2026-02-30', '2026-13-01',
      '2026-00-01', '2026-11-00', '2026-1-02', '2026-11-02T00:00:00.000Z', ' 2026-11-02']) {
      const f = fixture(); f.report.timing = { [field]: value };
      assert.deepEqual(createCatalogSelection(f.snapshot, f.references), { ok: false, code: 'catalog-unavailable' });
    }
  }
  const valid = fixture(); valid.report.timing = { completedDate: '2000-02-29' };
  assert.deepEqual(select(valid).evidenceReferences.historicalResearch[0].timing, { completedDate: '2000-02-29' });
});

test('completion minute requires its own date and strict HH:mm', () => {
  for (const timing of [{ completedMinuteUTC: '19:50' },
    { observedDate: '2026-11-02', completedMinuteUTC: '19:50' },
    ...['24:00', '19:60', '9:50', '19:5', '19:50:00', '19:50Z', '', null, undefined, 1950]
      .map(completedMinuteUTC => ({ completedDate: '2026-11-02', completedMinuteUTC }))]) {
    const f = fixture(); f.report.reportedAt = null; f.report.timing = timing;
    assert.deepEqual(createCatalogSelection(f.snapshot, f.references), { ok: false, code: 'catalog-unavailable' });
  }
  const valid = fixture(); valid.report.timing = { completedDate: '2026-11-02', completedMinuteUTC: '19:50' };
  assert.deepEqual(select(valid).evidenceReferences.historicalResearch[0].timing, valid.report.timing);
});

test('unknown timing never weakens exact occurrence binding or inactive finding checks', () => {
  const mutations = [f => { f.fieldKey = 'CPPA:2026:missing:website_raw'; },
    f => { f.candidateIndex = 0; }, f => { f.sourceSpan = [0, 21]; },
    f => { f.sourceToken = 'http://other.example'; }, f => { f.hostname = 'other.example'; },
    f => { f.actionable = true; }];
  for (const mutate of mutations) {
    const f = fixture(); delete f.report.reportedAt; mutate(f.report.findings[0]);
    assert.deepEqual(createCatalogSelection(f.snapshot, f.references), { ok: false, code: 'catalog-unavailable' });
  }
  const valid = fixture(); delete valid.report.reportedAt;
  assert.deepEqual(select(valid).evidenceReferences.historicalResearch[0].findings, valid.report.findings);
});

test('unknown timing retains required artifact attribution and report allowlist checks', () => {
  for (const mutate of [r => { delete r.artifact; }, r => { r.artifact.sha256 = 'bad'; },
    r => { r.artifact.bytes = 0; }, r => { delete r.attribution; }, r => { r.attribution = ''; },
    r => { r.extra = true; }]) {
    const f = fixture(); f.report.reportedAt = null; mutate(f.report);
    assert.deepEqual(createCatalogSelection(f.snapshot, f.references), { ok: false, code: 'catalog-unavailable' });
  }
  const valid = fixture(); valid.report.reportedAt = null;
  assert.deepEqual(select(valid).evidenceReferences.historicalResearch[0], valid.report);
});
