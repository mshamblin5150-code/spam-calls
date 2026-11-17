// Privileged input: successful output of the separately reviewed offline adapter.
// This module contains no acquisition, destination approval or personal workflow.
const unavailable = () => ({ ok: false, code: 'catalog-unavailable' });
function freeze(value) {
  if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
}
const hash = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const text = value => typeof value === 'string' && value.length > 0;
const calendarDate = value => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
const keys = (value, allowed) => value && typeof value === 'object' && !Array.isArray(value) && Object.keys(value).every(key => allowed.includes(key));
function requireEvidence(condition) { if (!condition) throw new Error('Invalid evidence reference'); }
function artifact(value) {
  return keys(value, ['label', 'sha256', 'bytes', 'libraryFileId', 'fileId', 'sourceThreadId', 'sourceMessageId']) && text(value.label) && hash(value.sha256) && Number.isSafeInteger(value.bytes) && value.bytes > 0 && ['libraryFileId', 'fileId', 'sourceThreadId', 'sourceMessageId'].every(key => value[key] === undefined || text(value[key]));
}
// Caller-attested references, not a parser or independent authentication of report bytes.
// Lexical hypotheses and dated historical observations never constitute destination consent.
function bindEvidence(snapshot, input) {
  const evidence = structuredClone(input);
  requireEvidence(keys(evidence, ['triage', 'research']) && Array.isArray(evidence.research));
  const fields = new Map();
  if (evidence.triage !== null) {
    const triage = evidence.triage;
    requireEvidence(keys(triage, ['artifact', 'source', 'method', 'fields']) && artifact(triage.artifact));
    requireEvidence(triage.source?.sha256 === snapshot.artifactSha256 && Array.isArray(triage.fields));
    requireEvidence(keys(triage.method, ['version', 'networkRequests', 'originalFieldsUnchanged', 'rule']) && triage.method.version === 'lexical-triage/1' && triage.method.networkRequests === 0 && triage.method.originalFieldsUnchanged === true && text(triage.method.rule));
    for (const field of triage.fields) {
      const observation = snapshot.observations[field.sourceRecordIndex];
      const link = field.field === 'website_raw' ? observation?.website : field.field === 'privacy_rights_url_raw' ? observation?.privacyRights : null;
      requireEvidence(keys(field, ['key', 'sourceRecordIndex', 'brokerId', 'brokerName', 'field', 'raw', 'originalReason', 'disposition', 'candidates', 'fieldVerification', 'actionable']) && Number.isSafeInteger(field.sourceRecordIndex) && observation && link);
      requireEvidence(field.brokerId === observation.sourceNativeId && field.key === `${observation.observationIdentity}:${field.field}` && !fields.has(field.key) && field.raw === link.raw);
      requireEvidence(field.actionable === false && field.fieldVerification === 'unverified' && text(field.disposition) && text(field.originalReason) && Array.isArray(field.candidates));
      field.candidates.forEach((candidate, index) => {
        requireEvidence(keys(candidate, ['candidateIndex', 'sourceSpan', 'sourceToken', 'status', 'scheme', 'hostname', 'proposedHttpsText', 'hasQuery', 'hasFragment', 'verification', 'actionable', 'reviewFlags']));
        const span = candidate.sourceSpan;
        requireEvidence(candidate.candidateIndex === index && Array.isArray(span) && span.length === 2 && span.every(Number.isSafeInteger) && span[0] >= 0 && span[1] >= span[0] && span[1] <= field.raw.length && field.raw.slice(span[0], span[1]) === candidate.sourceToken);
        if (candidate.status === 'empty-segment') {
          requireEvidence(keys(candidate, ['candidateIndex', 'sourceSpan', 'sourceToken', 'status', 'actionable', 'reviewFlags']) && span[0] === span[1] && candidate.sourceToken === '' && candidate.actionable === false && Array.isArray(candidate.reviewFlags) && candidate.reviewFlags.length === 0);
          const left = span[0] === 0 ? 0 : field.raw.lastIndexOf(';', span[0] - 1) + 1;
          const delimiter = field.raw.indexOf(';', span[0]);
          const right = delimiter < 0 ? field.raw.length : delimiter;
          requireEvidence(field.raw.slice(left, right).trim() === '' && field.raw.slice(0, left).split(';').length - 1 === index);
        } else {
          requireEvidence(text(candidate.sourceToken) && candidate.actionable === false && candidate.status === 'lexical-candidate-only' && candidate.verification === 'no-network-or-ownership-validation');
        }
      });
      fields.set(field.key, field);
    }
  }
  for (const report of evidence.research) {
    requireEvidence(keys(report, ['artifact', 'reportedAt', 'timing', 'attribution', 'findings']) && artifact(report.artifact) && text(report.attribution) && Array.isArray(report.findings));
    if (Object.hasOwn(report, 'reportedAt')) {
      requireEvidence(report.reportedAt === null || (text(report.reportedAt) && new Date(report.reportedAt).toISOString() === report.reportedAt));
    }
    if (Object.hasOwn(report, 'timing')) {
      const timing = report.timing;
      requireEvidence(keys(timing, ['observedDate', 'completedDate', 'completedMinuteUTC']) && Object.keys(timing).length > 0);
      for (const field of ['observedDate', 'completedDate']) {
        if (Object.hasOwn(timing, field)) requireEvidence(calendarDate(timing[field]));
      }
      if (Object.hasOwn(timing, 'completedMinuteUTC')) {
        requireEvidence(typeof timing.completedMinuteUTC === 'string' && /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(timing.completedMinuteUTC) && Object.hasOwn(timing, 'completedDate'));
      }
    }
    for (const finding of report.findings) {
      requireEvidence(keys(finding, ['fieldKey', 'candidateIndex', 'sourceSpan', 'sourceToken', 'hostname', 'outcome', 'actionable']));
      const candidate = fields.get(finding.fieldKey)?.candidates[finding.candidateIndex];
      requireEvidence(Number.isSafeInteger(finding.candidateIndex) && candidate && candidate.status === 'lexical-candidate-only' && JSON.stringify(finding.sourceSpan) === JSON.stringify(candidate.sourceSpan) && finding.sourceToken === candidate.sourceToken && finding.hostname === candidate.hostname);
      requireEvidence(finding.actionable === false && ['https-readable', 'unresolved', 'unreadable', 'not-visited'].includes(finding.outcome));
    }
  }
  return evidence;
}
export function createCatalogSelection(snapshot, references = { triage: null, research: [] }) {
  try {
  if (!snapshot?.ok || snapshot.parserVersion !== 'registry-flat/2' || snapshot.outputSchemaVersion !== 'registry-observation/1') return unavailable();
  snapshot = structuredClone(snapshot);
  const { organizations, observations } = snapshot;
  if (!Array.isArray(organizations) || !organizations.length || !Array.isArray(observations) || observations.length !== organizations.length || snapshot.acceptedCount !== organizations.length) return unavailable();
  if (new Set(organizations.map(item => item.observationIdentity)).size !== organizations.length) return unavailable();
  for (let index = 0; index < organizations.length; index++) {
    const organization = organizations[index]; const observation = observations[index];
    if (observation.observationIdentity !== organization.observationIdentity || observation.sourceNativeId !== organization.sourceNativeId || observation.sourceRecordIndex !== index || observation.website.actionable !== false || observation.privacyRights.actionable !== false) return unavailable();
  }
  const evidence = bindEvidence(snapshot, references);
  const entries = new Map(snapshot.organizations.map(organization => {
    const observation = snapshot.observations.find(item => item.observationIdentity === organization.observationIdentity);
    const lexicalTriage = evidence.triage ? { ...evidence.triage, fields: evidence.triage.fields.filter(item => item.brokerId === observation.sourceNativeId && item.sourceRecordIndex === observation.sourceRecordIndex) } : null;
    const fieldKeys = new Set(lexicalTriage?.fields.map(item => item.key) ?? []);
    const historicalResearch = evidence.research.map(report => ({ ...report, findings: report.findings.filter(item => fieldKeys.has(item.fieldKey)) })).filter(report => report.findings.length);
    return [organization.observationIdentity, freeze({
      identity: organization.observationIdentity, name: organization.name, aliases: organization.aliasesRaw,
      website: observation.website, privacyRights: observation.privacyRights,
      activation: 'held', triage: evidence.triage ? 'lexical-reference-attached' : 'not-reconciled',
      evidenceReferences: { lexicalTriage, historicalResearch, priorityPortalDiscrepancy: 'unknown', destinationApproval: 'none' },
      diagnostics: snapshot.diagnostics.filter(item => item.location.startsWith(`records[${observation.sourceRecordIndex}].`)),
      provenance: {
        artifactSha256: snapshot.artifactSha256, sourceSha256: snapshot.sourceMetadata.source_sha256,
        sourcePage: snapshot.sourceMetadata.source_page,
        sourceUpdated: snapshot.sourceMetadata.source_page_updated, retrievedOn: snapshot.sourceMetadata.retrieved_on,
        authority: observation.authority, registryYear: observation.registryYear, activityYear: observation.activityYear,
        sourceNativeId: observation.sourceNativeId, sourceRecordIndex: observation.sourceRecordIndex,
        fieldProvenance: observation.fieldProvenance,
      },
    })];
  }));
  return { ok: true, catalog: Object.freeze({
    choices: freeze([...entries.values()].map(item => ({ identity: item.identity, name: item.name }))),
    select(identity) {
      const broker = entries.get(identity);
      return broker ? { ok: true, broker } : { ok: false, code: 'unknown-broker' };
    },
  }) };
  } catch { return unavailable(); }
}
