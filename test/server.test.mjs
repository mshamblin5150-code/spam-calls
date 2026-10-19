import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from '../scripts/serve.mjs';

test('loopback server serves only app files, rejects mutations, and blocks outbound app requests', async () => {
  const server = createServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  try {
    const page = await fetch(origin);
    assert.equal(page.status, 200);
    assert.match(await page.text(), /Verify demo identity/);
    assert.match(page.headers.get('content-security-policy'), /connect-src 'none'/);
    assert.equal((await fetch(`${origin}/app/planner.mjs`)).status, 200);
    assert.equal((await fetch(`${origin}/.git/config`)).status, 404);
    assert.equal((await fetch(`${origin}/local-data/qa/concept.png`)).status, 404);
    assert.equal((await fetch(origin, { method: 'POST', body: 'demo' })).status, 405);
  } finally { await new Promise(resolve => server.close(resolve)); }
});
