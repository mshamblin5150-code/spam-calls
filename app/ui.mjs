import { cases, brokers, artifacts, eventKinds, statusFor, exportState } from './planner.mjs';
import { createStore, resetStore } from './storage.mjs';

const $ = id => document.getElementById(id);
let store;
let caseId = cases[0].id;
let brokerId = brokers[0].id;
let dataMode;
let pendingImport;

function option(value, label) { const node = document.createElement('option'); node.value = value; node.textContent = label; return node; }
function message(text, error = false) { $('message').textContent = text; $('message').classList.toggle('error', error); }
function errorText(error) { return error instanceof SyntaxError ? 'Invalid synthetic JSON. Nothing was changed.' : error.message; }
function clearApproval() { $('approval').checked = false; }
function locked(action) {
  if (!navigator.locks) return Promise.reject(new Error('This browser needs Web Locks support to save safely. Use a current browser on localhost.'));
  return navigator.locks.request('spam-calls-synthetic-demo-write', action);
}

function refreshEvidence() {
  clearApproval();
  $('artifact').replaceChildren(option('', 'Choose synthetic evidence'), ...artifacts.filter(item => item.brokerId === brokerId && item.type === $('event').value).map(item => option(item.id, item.label)));
  $('artifact-detail').textContent = 'Choose a matching synthetic evidence fixture.';
  $('approval-label').textContent = `I approve “${eventKinds.find(item => item.id === $('event').value).label}” for ${cases.find(item => item.id === caseId).label} and ${brokers.find(item => item.id === brokerId).label} only.`;
}

function render() {
  const broker = brokers.find(item => item.id === brokerId);
  const state = store?.state;
  $('broker-name').textContent = broker.label;
  $('broker-domain').textContent = broker.domain;
  $('event-fields').disabled = !store;
  $('export').disabled = !store;
  $('import').disabled = !store;
  $('brokers').replaceChildren(...brokers.map(item => {
    const button = document.createElement('button'); button.className = 'broker'; button.type = 'button';
    button.setAttribute('aria-pressed', String(item.id === brokerId));
    for (const [tag, cls, text] of [['strong', '', item.label], ['span', 'domain', item.domain], ['span', 'status', state ? `Simulated: ${statusFor(state, caseId, item.id)}` : 'Storage unavailable']]) {
      const node = document.createElement(tag); node.className = cls; node.textContent = text; button.append(node);
    }
    button.addEventListener('click', () => { brokerId = item.id; resetForm(); render(); $('broker-name').tabIndex = -1; $('broker-name').focus(); });
    return button;
  }));
  const events = state?.events.filter(event => event.caseId === caseId && event.brokerId === brokerId) ?? [];
  $('item-status').textContent = state ? `Simulated status: ${statusFor(state, caseId, brokerId)}. This never proves a real removal.` : 'History unavailable. Reload or explicitly reset demo storage.';
  $('timeline').replaceChildren(...events.map(event => {
    const artifact = artifacts.find(item => item.id === event.artifactId);
    const li = document.createElement('li');
    const title = document.createElement('strong'); title.textContent = eventKinds.find(item => item.id === event.type).label;
    const observation = document.createElement('p'); observation.textContent = artifact.observation;
    const evidence = document.createElement('small'); evidence.textContent = `Evidence: ${artifact.id} · ${event.timestamp}`;
    const identity = document.createElement('small'); identity.textContent = `Demo identity: ${event.identity} · Explicit approval recorded · ${event.id}`;
    li.append(title, observation, evidence, identity);
    if (event.supersedes) { const correction = document.createElement('small'); correction.textContent = `Supersedes ${event.supersedes}; original event retained.`; li.append(correction); }
    return li;
  }));
  if (!events.length) { const li = document.createElement('li'); li.className = 'empty'; li.textContent = store ? 'No simulated events yet.' : 'Demo history could not be loaded.'; $('timeline').append(li); }
  $('persistence').textContent = store ? 'Saved on this device after each recorded event. Synthetic fixtures only.' : 'Local storage unavailable. No new events can be recorded.';
}

function resetForm() { $('event-form').reset(); refreshEvidence(); }

$('case').replaceChildren(...cases.map(item => option(item.id, item.label)));
$('identity').append(...cases.map(item => option(item.id, item.label)));
$('event').replaceChildren(...eventKinds.map(item => option(item.id, item.label)));
$('case').addEventListener('change', () => { caseId = $('case').value; resetForm(); render(); });
$('identity').addEventListener('change', clearApproval);
$('event').addEventListener('change', refreshEvidence);
$('artifact').addEventListener('change', () => { clearApproval(); $('artifact-detail').textContent = artifacts.find(item => item.id === $('artifact').value)?.observation ?? 'Choose a matching synthetic evidence fixture.'; });
$('event-form').addEventListener('submit', async event => {
  event.preventDefault();
  const command = { id: `event-${crypto.randomUUID()}`, timestamp: new Date().toISOString(), caseId, brokerId, identity: $('identity').value, approved: $('approval').checked, type: $('event').value, artifactId: $('artifact').value };
  if (command.type === 'correction') command.supersedes = store.state.events.findLast(item => item.caseId === caseId && item.brokerId === brokerId)?.id ?? null;
  clearApproval();
  $('event-fields').disabled = true;
  try {
    await locked(() => store.record(command));
    resetForm(); render(); message('Simulated event saved with its synthetic evidence. Nothing was sent.');
  } catch (error) { render(); message(errorText(error), true); }
});

function openData(mode) {
  dataMode = mode; pendingImport = null;
  $('data-title').textContent = mode === 'export' ? 'Preview synthetic export' : 'Import synthetic demo';
  $('data-help').textContent = mode === 'export' ? 'Review all demo cases and evidence events before downloading. This file contains only fixture records.' : 'Paste a synthetic export from this demo. No names, contact details, or arbitrary evidence are accepted. Validation changes nothing until you apply it.';
  $('data-text').readOnly = mode === 'export';
  $('data-text').value = mode === 'export' ? store.export() : '';
  $('data-action').textContent = mode === 'export' ? 'Download synthetic JSON' : 'Preview import';
  $('dialog-message').textContent = '';
  $('data-dialog').showModal();
}
$('export').addEventListener('click', () => openData('export'));
$('import').addEventListener('click', () => openData('import'));
$('close-dialog').addEventListener('click', () => $('data-dialog').close());
$('data-text').addEventListener('input', () => { pendingImport = null; $('data-action').textContent = 'Preview import'; $('dialog-message').textContent = ''; });
$('data-action').addEventListener('click', async () => {
  try {
    if (dataMode === 'export') {
      const link = document.createElement('a');
      const url = URL.createObjectURL(new Blob([store.export()], { type: 'application/json' }));
      link.href = url; link.download = 'spam-calls-synthetic-demo.json'; link.click(); URL.revokeObjectURL(url);
      $('data-dialog').close(); message('Synthetic export downloaded.');
    } else if (pendingImport) {
      await locked(() => store.import(pendingImport));
      $('data-dialog').close(); resetForm(); render(); message('Validated synthetic history imported. Duplicate events were kept once.');
    } else {
      const next = store.previewImport($('data-text').value);
      pendingImport = exportState(next);
      $('data-text').value = pendingImport;
      $('dialog-message').textContent = `Validated preview: ${next.events.length} total synthetic events after import. Existing history is still unchanged.`;
      $('data-action').textContent = 'Apply validated import';
    }
  } catch (error) { pendingImport = null; $('data-action').textContent = dataMode === 'export' ? 'Download synthetic JSON' : 'Preview import'; $('dialog-message').textContent = errorText(error); }
});
$('reset').addEventListener('click', () => $('reset-dialog').showModal());
$('cancel-reset').addEventListener('click', () => $('reset-dialog').close());
$('confirm-reset').addEventListener('click', async () => {
  try { await locked(() => { store = resetStore(localStorage, true); }); $('reset-dialog').close(); resetForm(); render(); message('All demo history reset. No external data was changed.'); }
  catch (error) { $('reset-dialog').close(); message(errorText(error), true); }
});
window.addEventListener('storage', () => { clearApproval(); message('Demo storage may have changed in another tab. Reload before continuing.', true); });
try { store = createStore(localStorage); }
catch (error) { message(`Cannot load demo storage: ${errorText(error)} Existing data was not replaced.`, true); }
resetForm(); render();
