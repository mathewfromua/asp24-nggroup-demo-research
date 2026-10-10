// Vite owns the module graph, transforms, CSS splitting and asset fingerprinting.
// This small wrapper adds the existing static publication contract after compilation.
import {readFileSync, writeFileSync, readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {build} from 'vite';
import {getDeploymentConfig} from './deployment-config.mjs';
import {buildPublication} from './build-publication.mjs';

const config = getDeploymentConfig();
await build();
const manifest = JSON.parse(readFileSync('dist/vite-manifest.json', 'utf8'));
const entry = name => {
  const record = manifest[name];
  if (!record?.isEntry || !record.file.startsWith('assets/')) throw new Error(`Missing compiled entry: ${name}`);
  return record.file.slice('assets/'.length);
};
let html = readFileSync('dist/index.html', 'utf8');
if (html.includes('name="app-base-path"')) throw new Error('Build owns app-base-path metadata');
html = html.replace('</head>', `<meta name="app-base-path" content="${config.BASE_PATH}"></head>`);
writeFileSync('dist/demo.html', html);
buildPublication(config, entry('hub.css'), entry('legacy-entry.js'));
writeFileSync('dist/build-config.json', JSON.stringify(config, null, 2) + '\n');
const generated = readdirSync('dist/assets').filter(name => /-[a-f0-9]{12}\.(?:js|css)$/.test(name)).sort();
const files = Object.fromEntries(generated.map(name => {
  const bytes = readFileSync(`dist/assets/${name}`);
  return [`assets/${name}`, {bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')}];
}));
writeFileSync('dist/asset-integrity.json', JSON.stringify({schemaVersion: 1, builder: 'vite', files}, null, 2) + '\n');
console.log(`Static publication: Vite module graph; ${generated.length} compiled assets; base ${config.BASE_PATH}.`);
