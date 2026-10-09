// Reproducible native-ESM build; no runtime or build dependencies and no network.
import {readFileSync, writeFileSync, rmSync, mkdirSync, cpSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve, dirname, basename, extname, relative} from 'node:path';
import {getDeploymentConfig} from './deployment-config.mjs';
import {buildPublication} from './build-publication.mjs';
import {assetUrl} from '../asset-url.js';

const root = resolve('.'), out = resolve('dist'), emitted = new Map();
const config = getDeploymentConfig();
rmSync(out, {recursive: true, force: true});
mkdirSync(resolve(out, 'assets'), {recursive: true});
cpSync(resolve(root, 'public'), out, {recursive: true});
const fingerprint = text => createHash('sha256').update(text).digest('hex').slice(0, 12);
function emit(source) {
  const path = resolve(root, source);
  if (!path.startsWith(root + '/')) throw new Error('Invalid local dependency');
  if (emitted.has(path)) return emitted.get(path);
  let text = readFileSync(path, 'utf8');
  if (extname(path) === '.js') {
    text = text.replace(/(\bfrom\s*['"])(\.\.?\/[^'"]+)(['"])/g, (_, start, dependency, end) =>
      `${start}./${emit(relative(root, resolve(dirname(path), dependency)))}${end}`);
  }
  if (extname(path) === '.js') text = text.replace(/(\bimport\(['"])(\.\.?\/[^'"]+)(['"]\))/g, (_, start, dependency, end) => `${start}./${emit(relative(root, resolve(dirname(path), dependency)))}${end}`);
  const extension = extname(path), name = `${basename(path, extension)}-${fingerprint(text)}${extension}`;
  writeFileSync(resolve(out, 'assets', name), text);
  emitted.set(path, name);
  return name;
}
let html = readFileSync('index.html', 'utf8');
for (const file of ['style.css', 'finish.css', 'catalog.css', 'science.css', 'demo-entry.js']) {
  html = html.replace(`/${file}`, `/assets/${emit(file)}`);
}
html = html.replace(/((?:src|href)=")\/(?!\/)([^"#]+)(")/g, (_, start, path, end) =>
  `${start}${assetUrl(path, config.BASE_PATH)}${end}`);
if (html.includes('name="app-base-path"')) throw new Error('Build owns app-base-path metadata');
html = html.replace('</head>', `<meta name="app-base-path" content="${config.BASE_PATH}"></head>`);
writeFileSync(resolve(out, 'demo.html'), html);
buildPublication(config,emit('hub.css'),emit('legacy-entry.js'));
writeFileSync(resolve(out, 'build-config.json'), JSON.stringify(config, null, 2) + '\n');
console.log(`Static build: ${emitted.size} fingerprinted source files; base ${config.BASE_PATH}.`);
