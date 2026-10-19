import test from 'node:test';
import assert from 'node:assert/strict';
import { emptyState, recordEvent, statusFor, exportState, importState } from '../app/planner.mjs';

const command = (type = 'submission', overrides = {}) => ({
  id: 'event-001', timestamp: '2026-10-19T10:00:00.000Z', caseId: 'demo-a',
  brokerId: 'cedar', identity: 'demo-a', approved: true, type,
  artifactId: `cedar-${type}`, ...overrides,
});

test('recording a matching approved synthetic receipt advances only its plan item', () => {
  const before = emptyState();
  const after = recordEvent(before, command());
  assert.equal(statusFor(after, 'demo-a', 'cedar'), 'simulated-submission');
  assert.equal(statusFor(after, 'demo-a', 'harbor'), 'planned');
  assert.equal(before.events.length, 0);
  assert.equal(after.events[0].artifactId, 'cedar-submission');
});

test('identity, one-step approval, evidence and transition guards reject unsafe commands', () => {
  for (const [overrides, expected] of [
    [{ identity: 'demo-b' }, /matching demo identity/],
    [{ approved: false }, /Explicit approval/],
    [{ approved: 'true' }, /Explicit approval/],
    [{ artifactId: 'harbor-submission' }, /matching synthetic evidence/],
    [{ type: 'confirmation', artifactId: 'cedar-confirmation' }, /Unsupported status transition/],
    [{ type: 'toString', artifactId: 'cedar-confirmation' }, /Unknown event type/],
    [{ caseId: 'real-person' }, /Only known synthetic/],
    [{ timestamp: '2026-02-30T10:00:00.000Z' }, /Invalid timestamp/],
    [{ note: 'arbitrary input' }, /unknown or missing fields/],
  ]) {
    const state = emptyState();
    assert.throws(() => recordEvent(state, command('submission', overrides)), expected);
    assert.deepEqual(state, { schemaVersion: 1, fixtureSet: 'demo-v1', events: [] });
  }
});

function completedWorkflow() {
  let state = recordEvent(emptyState(), command());
  state = recordEvent(state, command('awaiting', { id: 'event-002' }));
  return recordEvent(state, command('confirmation', { id: 'event-003' }));
}

test('confirmation requires the ordered fixture trail and a correction retains that trail', () => {
  const confirmed = completedWorkflow();
  assert.equal(statusFor(confirmed, 'demo-a', 'cedar'), 'simulated-confirmed');
  const corrected = recordEvent(confirmed, command('correction', { id: 'event-004', supersedes: 'event-003' }));
  assert.equal(statusFor(corrected, 'demo-a', 'cedar'), 'unresolved');
  assert.deepEqual(corrected.events.map(event => [event.id, event.type, event.supersedes]), [
    ['event-001', 'submission', null], ['event-002', 'awaiting', null],
    ['event-003', 'confirmation', null], ['event-004', 'correction', 'event-003'],
  ]);
  assert.throws(() => recordEvent(confirmed, command('correction', { id: 'event-005', supersedes: 'event-001' })), /last event/);
  assert.throws(() => recordEvent(emptyState(), command('correction')), /last event/);
  assert.throws(() => recordEvent(confirmed, command('issue', { id: 'event-005', timestamp: '2026-10-18T10:00:00.000Z' })), /precedes/);
});

test('export and import preserve history and repeated import is idempotent', () => {
  const original = completedWorkflow();
  const reopened = importState(emptyState(), exportState(original));
  assert.equal(statusFor(reopened, 'demo-a', 'cedar'), 'simulated-confirmed');
  assert.deepEqual(reopened.events.map(event => event.id), ['event-001', 'event-002', 'event-003']);
  assert.deepEqual(importState(reopened, exportState(original)), reopened);
  const reorderedKeys = JSON.stringify(original, Object.keys(original));
  assert.throws(() => importState(emptyState(), reorderedKeys), /unknown or missing fields/);
});

test('malformed, unsupported, forged, conflicting and oversized imports cannot mutate state', () => {
  const state = recordEvent(emptyState(), command());
  const before = exportState(state);
  const conflict = JSON.parse(before);
  conflict.events[0].timestamp = '2026-10-19T11:00:00.000Z';
  const forged = JSON.parse(before);
  forged.events[0].status = 'simulated-confirmed';
  const unsupported = JSON.parse(before);
  unsupported.schemaVersion = 99;
  for (const text of ['{', JSON.stringify(unsupported), JSON.stringify(forged), JSON.stringify(conflict), ' '.repeat(1_000_001)]) {
    assert.throws(() => importState(state, text));
    assert.equal(exportState(state), before);
  }
});

test('public status lookup rejects invented confirmation without validated history', () => {
  assert.throws(() => statusFor({ events: [{ caseId: 'demo-a', brokerId: 'cedar', type: 'confirmation' }] }, 'demo-a', 'cedar'), /unknown or missing fields/);
  assert.equal(statusFor(completedWorkflow(), 'demo-a', 'cedar'), 'simulated-confirmed');
});

test('reordering imported JSON fields still deduplicates an identical event', () => {
  const original = completedWorkflow();
  const reordered = { ...original, events: original.events.map(event => Object.fromEntries(Object.entries(event).reverse())) };
  const merged = importState(original, JSON.stringify(reordered));
  assert.deepEqual(merged.events.map(event => event.id), ['event-001', 'event-002', 'event-003']);
  assert.equal(statusFor(merged, 'demo-a', 'cedar'), 'simulated-confirmed');
});
