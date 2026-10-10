// Preview only: serves the built public directory at its actual deployment prefix.
import http from 'node:http';
import {readFile, realpath, stat} from 'node:fs/promises';
import {readFileSync} from 'node:fs';
import {resolve, extname} from 'node:path';
import {normalizeBasePath} from './deployment-config.mjs';

const args = process.argv.slice(2);
const option = name => {const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined;};
const root = await realpath(resolve('dist'));
const port = Number(option('--port') || process.env.PORT || 8000);
const host = option('--host') || '127.0.0.1';
const config = JSON.parse(readFileSync(resolve(root, 'build-config.json'), 'utf8'));
const basePath = normalizeBasePath(option('--base-path') || config.BASE_PATH);
if (basePath !== config.BASE_PATH) throw new Error('Preview path must match the build; rebuild with BASE_PATH first');
if (!Number.isInteger(port) || port < 1 || port > 65535 || !['127.0.0.1', '0.0.0.0', 'localhost'].includes(host)) throw new Error('Invalid preview host or port');
const types = {'.txt':'text/plain; charset=utf-8','.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.svg':'image/svg+xml', '.webp':'image/webp', '.png':'image/png', '.pdf':'application/pdf', '.json':'application/json; charset=utf-8'};
http.createServer(async (req, res) => {
  try {
    if (!['GET', 'HEAD'].includes(req.method)) {res.writeHead(405); res.end(); return;}
    const url = new URL(req.url, 'http://localhost');
    if (basePath !== '/' && url.pathname === basePath.slice(0, -1)) {
      res.writeHead(308, {Location: basePath + url.search}); res.end(); return;
    }
    const pathname = decodeURIComponent(url.pathname);
    if (!pathname.startsWith(basePath)) throw new Error('Outside deployment path');
    const relative = (pathname.slice(basePath.length) || '') + (pathname.endsWith('/') ? 'index.html' : '');
    const path = await realpath(resolve(root, relative));
    if (!path.startsWith(root + '/') || !(await stat(path)).isFile()) throw new Error('Invalid public file');
    const bytes = await readFile(path);
    res.writeHead(200, {'Content-Type': types[extname(path)] || 'application/octet-stream', 'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff'});
    res.end(req.method === 'HEAD' ? undefined : bytes);
  } catch {
    res.writeHead(404, {'Content-Type':'text/plain; charset=utf-8'}); res.end(req.method === 'HEAD' ? undefined : 'Not found');
  }
}).listen(port, host, () => console.log(`Preview: http://${host}:${port}${basePath}`));
