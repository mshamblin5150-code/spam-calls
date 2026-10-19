import { emptyState, exportState, importState, recordEvent, validateState } from './planner.mjs';

export const storageKey = 'spam-calls-synthetic-demo-v1';

export function resetStore(storage, approved) {
  if (approved !== true) throw new Error('Confirm reset before replacing demo history.');
  storage.setItem(storageKey, exportState(emptyState()));
  return createStore(storage);
}

export function createStore(storage) {
  let baseline = storage.getItem(storageKey);
  let state = baseline === null ? emptyState() : importState(emptyState(), baseline);
  function save(next) {
    const valid = validateState(next);
    if (storage.getItem(storageKey) !== baseline) throw new Error('Demo storage changed in another tab. Reload before continuing.');
    const text = exportState(valid);
    storage.setItem(storageKey, text);
    baseline = text;
    state = valid;
    return structuredClone(state);
  }
  return {
    get state() { return structuredClone(state); },
    record(command) { return save(recordEvent(state, command)); },
    import(text) { return save(importState(state, text)); },
    previewImport(text) { return importState(state, text); },
    export() { return exportState(state); },
  };
}
