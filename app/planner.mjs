export const cases = Object.freeze([
  Object.freeze({ id: 'demo-a', label: 'Demo Case A' }),
  Object.freeze({ id: 'demo-b', label: 'Demo Case B' }),
]);
export const brokers = Object.freeze([
  Object.freeze({ id: 'cedar', label: 'Cedar Directory', domain: 'cedar.example' }),
  Object.freeze({ id: 'harbor', label: 'Harbor Index', domain: 'harbor.example' }),
]);

const kinds = {
  submission: { label: 'Simulated submission', status: 'simulated-submission', from: ['planned', 'unresolved'], observation: 'Invented submission receipt recorded. Nothing was sent.' },
  awaiting: { label: 'Await simulated confirmation', status: 'awaiting-simulated-confirmation', from: ['simulated-submission'], observation: 'Invented pending notice recorded. No mailbox was accessed.' },
  confirmation: { label: 'Simulated confirmation', status: 'simulated-confirmed', from: ['awaiting-simulated-confirmation'], observation: 'Invented confirmation receipt recorded. No real removal is proved.' },
  issue: { label: 'Mark simulated issue', status: 'unresolved', from: ['planned', 'simulated-submission', 'awaiting-simulated-confirmation', 'simulated-confirmed', 'unresolved'], observation: 'Invented discrepancy recorded. The plan item needs review.' },
  correction: { label: 'Correct last simulated event', status: 'unresolved', observation: 'Invented correction supersedes the last event. Original history is retained.' },
};
export const eventKinds = Object.freeze(Object.entries(kinds).map(([id, value]) => Object.freeze({ id, label: value.label })));
export const artifacts = Object.freeze(brokers.flatMap(broker => Object.entries(kinds).map(([type, value]) => Object.freeze({
  id: `${broker.id}-${type}`, brokerId: broker.id, type, label: `${broker.label}: ${value.label.toLowerCase()} fixture`, observation: value.observation,
}))));

export function emptyState() { return { schemaVersion: 1, fixtureSet: 'demo-v1', events: [] }; }

function requireValue(condition, message) { if (!condition) throw new Error(message); }
function exactKeys(value, keys, label) {
  requireValue(value !== null && typeof value === 'object' && !Array.isArray(value), `${label} must be an object.`);
  requireValue(Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key)), `${label} has unknown or missing fields.`);
}
const eventKeys = ['schemaVersion', 'id', 'timestamp', 'caseId', 'brokerId', 'identity', 'approved', 'type', 'artifactId', 'supersedes'];

function appendValidated(state, event) {
  exactKeys(event, eventKeys, 'Event');
  requireValue(event.schemaVersion === 1, 'Unsupported event schema.');
  requireValue(typeof event.id === 'string' && /^event-[a-z0-9-]{3,64}$/.test(event.id), 'Invalid event ID.');
  requireValue(!state.events.some(existing => existing.id === event.id), 'Duplicate event ID.');
  requireValue(typeof event.timestamp === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(event.timestamp) && Number.isFinite(Date.parse(event.timestamp)) && new Date(event.timestamp).toISOString() === event.timestamp, 'Invalid timestamp.');
  requireValue(cases.some(item => item.id === event.caseId) && brokers.some(item => item.id === event.brokerId), 'Only known synthetic cases and brokers are accepted.');
  requireValue(event.identity === event.caseId, 'Select the matching demo identity.');
  requireValue(event.approved === true, 'Explicit approval is required for this simulated step.');
  const kind = Object.hasOwn(kinds, event.type) ? kinds[event.type] : null;
  requireValue(kind, 'Unknown event type.');
  const artifact = artifacts.find(item => item.id === event.artifactId);
  requireValue(artifact && artifact.brokerId === event.brokerId && artifact.type === event.type, 'Select matching synthetic evidence for this broker and event.');
  const previous = state.events.findLast(item => item.caseId === event.caseId && item.brokerId === event.brokerId);
  requireValue(!previous || event.timestamp >= previous.timestamp, 'Event time precedes existing history.');
  if (event.type === 'correction') {
    requireValue(previous && event.supersedes === previous.id, 'Correction must supersede the last event for this plan item.');
  } else {
    requireValue(event.supersedes === null, 'Only a correction may supersede an event.');
    requireValue(kind.from.includes(statusFor(state, event.caseId, event.brokerId)), 'Unsupported status transition.');
  }
  return { ...state, events: [...state.events, { ...event }] };
}

export function validateState(value) {
  exactKeys(value, ['schemaVersion', 'fixtureSet', 'events'], 'State');
  requireValue(value.schemaVersion === 1 && value.fixtureSet === 'demo-v1', 'Unsupported state schema or fixture set.');
  requireValue(Array.isArray(value.events) && value.events.length <= 1000, 'Event limit is 1000.');
  return value.events.reduce(appendValidated, emptyState());
}

export function recordEvent(state, command) {
  const valid = validateState(state);
  exactKeys(command, eventKeys.filter(key => key !== 'schemaVersion' && key !== 'supersedes').concat(Object.hasOwn(command, 'supersedes') ? ['supersedes'] : []), 'Command');
  requireValue(valid.events.length < 1000, 'Event limit is 1000.');
  return appendValidated(valid, { schemaVersion: 1, supersedes: null, ...command });
}

export function statusFor(state, caseId, brokerId) {
  const last = state.events.findLast(event => event.caseId === caseId && event.brokerId === brokerId);
  return last ? kinds[last.type].status : 'planned';
}

export function exportState(state) { return JSON.stringify(validateState(state), null, 2); }

export function importState(state, text) {
  requireValue(typeof text === 'string' && text.length <= 1_000_000, 'Import must be JSON text under 1 MB.');
  const incoming = validateState(JSON.parse(text));
  let merged = validateState(state);
  for (const event of incoming.events) {
    const existing = merged.events.find(item => item.id === event.id);
    if (existing) {
      requireValue(JSON.stringify(existing) === JSON.stringify(event), 'Conflicting event ID; import was not applied.');
    } else {
      requireValue(merged.events.length < 1000, 'Event limit is 1000.');
      merged = appendValidated(merged, event);
    }
  }
  return merged;
}
