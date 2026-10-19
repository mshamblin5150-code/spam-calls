import http from 'node:http';
import { readFile } from 'node:fs/promises';

const routes = new Map([
  ['/', ['../index.html', 'text/html; charset=utf-8']],
  ['/app/style.css', ['../app/style.css', 'text/css; charset=utf-8']],
  ['/app/ui.mjs', ['../app/ui.mjs', 'text/javascript; charset=utf-8']],
  ['/app/planner.mjs', ['../app/planner.mjs', 'text/javascript; charset=utf-8']],
  ['/app/storage.mjs', ['../app/storage.mjs', 'text/javascript; charset=utf-8']],
]);
export function createServer() {
  return http.createServer(async (request, response) => {
    const route = routes.get(request.url);
    const allowed = request.method === 'GET' || request.method === 'HEAD';
    response.setHeader('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; img-src data:; connect-src 'none'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'");
    response.setHeader('X-Content-Type-Options', 'nosniff');
    response.setHeader('Referrer-Policy', 'no-referrer');
    response.setHeader('Cache-Control', 'no-store');
    if (!route || !allowed) { response.writeHead(allowed ? 404 : 405); response.end('Unavailable'); return; }
    try {
      const content = await readFile(new URL(route[0], import.meta.url));
      response.writeHead(200, { 'Content-Type': route[1] });
      response.end(request.method === 'HEAD' ? undefined : content);
    } catch { response.writeHead(500); response.end('Local app file unavailable'); }
  });
}
if (process.argv[1] && import.meta.url === new URL(`file:///${process.argv[1].replaceAll('\\', '/')}`).href) {
  const server = createServer();
  server.on('error', error => { console.error(`Local demo server: ${error.message}`); process.exitCode = 1; });
  server.listen(4173, '127.0.0.1', () => console.log('Offline synthetic demo: http://127.0.0.1:4173 — Ctrl+C to stop'));
}
