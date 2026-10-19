import test from 'node:test';
import assert from 'node:assert/strict';
import { createStore, resetStore, storageKey } from '../app/storage.mjs';

function memoryStorage(initial = null) {
  let value = initial;
  return { getItem: () => value, setItem: (_key, text) => { value = text; } };
}
const command = { id: 'event-100', timestamp: '2026-10-19T10:00:00.000Z', caseId: 'demo-a', brokerId: 'cedar', identity: 'demo-a', approved: true, type: 'submission', artifactId: 'cedar-submission' };

test('approved events survive a new store instance on the same device', () => {
  const disk = memoryStorage();
  const store = createStore(disk);
  store.record(command);
  const reopened = createStore(disk);
  assert.equal(reopened.state.events[0].id, 'event-100');
  assert.equal(reopened.state.events[0].approved, true);
});

test('failed writes leave both the view and persisted history unchanged', () => {
  const disk = memoryStorage();
  disk.setItem = () => { throw new Error('Quota exceeded'); };
  const store = createStore(disk);
  assert.throws(() => store.record(command), /Quota exceeded/);
  assert.equal(store.state.events.length, 0);
  assert.equal(disk.getItem(storageKey), null);
});

test('corrupt storage fails closed and only an approved reset can recover it', () => {
  const disk = memoryStorage('{broken');
  assert.throws(() => createStore(disk));
  assert.throws(() => resetStore(disk, false), /Confirm reset/);
  assert.equal(disk.getItem(storageKey), '{broken');
  const recovered = resetStore(disk, true);
  recovered.record(command);
  assert.equal(createStore(disk).state.events[0].id, 'event-100');
});

test('stale writers and invalid imports cannot overwrite another tab', () => {
  const disk = memoryStorage();
  const first = createStore(disk);
  const stale = createStore(disk);
  first.record(command);
  const saved = disk.getItem(storageKey);
  assert.throws(() => stale.record({ ...command, id: 'event-101' }), /another tab/);
  assert.throws(() => first.import('{bad'));
  assert.equal(disk.getItem(storageKey), saved);
  assert.equal(stale.state.events.length, 0);
  assert.equal(createStore(disk).state.events.length, 1);
});

test('preview has no side effects, idempotent import persists once, and snapshots are isolated', () => {
  const source = createStore(memoryStorage());
  source.record(command);
  const disk = memoryStorage();
  const target = createStore(disk);
  assert.equal(target.previewImport(source.export()).events[0].id, 'event-100');
  assert.equal(disk.getItem(storageKey), null);
  target.import(source.export());
  target.import(source.export());
  const snapshot = target.state;
  snapshot.events[0].identity = 'changed';
  assert.equal(createStore(disk).state.events.length, 1);
  assert.equal(target.state.events[0].identity, 'demo-a');
});

test('unavailable storage is reported rather than silently replaced', () => {
  assert.throws(() => createStore({ getItem() { throw new Error('Access denied'); } }), /Access denied/);
});
