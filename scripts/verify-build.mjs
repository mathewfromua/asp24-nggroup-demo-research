/** Verify deploy contents, module references and exact approved reports. No network required. */
import {readdirSync,readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import assert from 'node:assert/strict';
import {publicationFiles} from './build-publication.mjs';
import {normalizeBasePath} from './deployment-config.mjs';
const walk=(dir,base='')=>readdirSync(dir,{withFileTypes:true}).flatMap(x=>x.isDirectory()?walk(`${dir}/${x.name}`,`${base}${x.name}/`):[`${base}${x.name}`]).sort();
const publicFiles=['vendor-licenses.txt','assets/research-social.png','assets/asp24-original.webp','assets/ng-original.svg','design-tokens.css','favicon.svg','reports/ASP24_Review.pdf','reports/NGGroup_Review.pdf',...JSON.parse(readFileSync('reports/html-public-assets.json','utf8'))].sort();
const pdfManifest=JSON.parse(readFileSync('reports/pdf-manifest.json','utf8'));
const expectedPDFs=Object.fromEntries(pdfManifest.map(r=>[r.file.startsWith('ASP24')?'ASP24_Review.pdf':'NGGroup_Review.pdf',r.sha256]));
const sha=b=>createHash('sha256').update(b).digest('hex');
assert.deepEqual(walk('public'),publicFiles,'Unapproved public file');
const contentHash=sha(readFileSync('reports/content.json'));
const reportInputs=JSON.parse(readFileSync('reports/input-manifest.json','utf8'));
for (const [file,digest] of Object.entries(reportInputs.files)) assert.equal(sha(readFileSync(file)),digest,`Outdated report generator input: ${file}`);
for (const report of [...pdfManifest,...JSON.parse(readFileSync('reports/html-manifest.json','utf8'))]) assert.equal(report.input_digest,reportInputs.digest,'Report input digest mismatch');
assert.equal(pdfManifest.length,2,'Expected two report PDF records');
for(const report of pdfManifest) assert.equal(report.content_sha256,contentHash,'PDF built from outdated content');
for(const report of JSON.parse(readFileSync('reports/html-manifest.json','utf8'))){
 assert.equal(report.content_sha256,contentHash,'HTML built from outdated content');
 const bytes=readFileSync(report.html);
 assert.equal(sha(bytes),report.sha256,'HTML hash');
 assert.ok(bytes.toString().includes(`name="report-source-sha256" content="${contentHash}"`));
 assert.match(bytes.toString(),/<html lang="uk">/);
}
const files=walk('dist');
const deploy=JSON.parse(readFileSync('dist/build-config.json','utf8'));
assert.equal(normalizeBasePath(deploy.BASE_PATH), deploy.BASE_PATH);
assert.equal(new URL(deploy.PUBLIC_BASE_URL).pathname, deploy.BASE_PATH);
assert.equal(new URL(deploy.PUBLIC_BASE_URL).protocol, 'https:');
// Vite bundles several source modules into chunks; validate the emitted graph and
// cryptographic bytes instead of requiring the former one-file-per-source layout.
const generated=/^assets\/[A-Za-z0-9_-]+-[a-f0-9]{12}\.(js|css)$/;
const viteManifest=JSON.parse(readFileSync('dist/vite-manifest.json','utf8'));
const integrity=JSON.parse(readFileSync('dist/asset-integrity.json','utf8'));
assert.equal(integrity.schemaVersion,1);assert.equal(integrity.builder,'vite');
const compiled=files.filter(p=>generated.test(p));
assert.deepEqual(Object.keys(integrity.files).sort(),compiled,'Compiled asset inventory');
assert.deepEqual(files.filter(p=>!['index.html','build-config.json','vite-manifest.json','asset-integrity.json',...publicationFiles(JSON.parse(readFileSync('publication.json','utf8')))].includes(p)&&!generated.test(p)),publicFiles,'Unexpected deployed file');
for(const name of ['index.html','legacy-entry.js','hub.css'])assert.equal(viteManifest[name]?.isEntry,true,`Compiled entry ${name}`);
assert.equal(viteManifest['app.js']?.isDynamicEntry,true,'Demo application stays a dynamic entry');
assert.ok(viteManifest['index.html'].css?.length,'Compiled demo styles');
const workbench='src/ui/comparison-workbench.tsx';
assert.equal(viteManifest[workbench]?.isDynamicEntry,true,'React workbench is a lazy entry');
assert.ok(viteManifest[workbench].css?.length,'Workbench styles stay with the lazy component');
const initialDependencies=new Set();
function visitInitial(name){
 if(initialDependencies.has(name))return;
 initialDependencies.add(name);
 for(const dependency of viteManifest[name]?.imports||[])visitInitial(dependency);
}
visitInitial('index.html');visitInitial('app.js');
assert.ok(!initialDependencies.has(workbench),'Catalog startup must not preload the React workbench');
assert.deepEqual(viteManifest['legacy-entry.js'].imports||[],[],'Report hub must not preload demo dependencies');
assert.deepEqual(viteManifest['legacy-entry.js'].dynamicImports||[],[],'Report hub must not load a catalog chunk');
const manifestFiles=new Set();
for(const [name,record] of Object.entries(viteManifest)){
 for(const file of [record.file,...(record.css||[]),...(record.assets||[])]){
  assert.ok(generated.test(file),`Unexpected compiled resource: ${file}`);
  assert.ok(files.includes(file),`Missing compiled resource: ${file}`);manifestFiles.add(file);
 }
 for(const dependency of [...(record.imports||[]),...(record.dynamicImports||[])])assert.ok(viteManifest[dependency],`Broken module graph: ${name} → ${dependency}`);
}
assert.deepEqual([...manifestFiles].sort(),compiled,'Unreferenced compiled output');
for(const f of publicFiles)assert.equal(sha(readFileSync(`public/${f}`)),sha(readFileSync(`dist/${f}`)),f);
for(const [f,hash]of Object.entries(expectedPDFs)){const pdf=readFileSync(`dist/reports/${f}`);assert.equal(pdf.subarray(0,5).toString(),'%PDF-',f);assert.equal(sha(pdf),hash,f);}
for(const f of compiled){
 const bytes=readFileSync(`dist/${f}`),expected=integrity.files[f];
 assert.equal(bytes.length,expected.bytes,`Asset byte length ${f}`);
 assert.equal(sha(bytes),expected.sha256,`Asset integrity ${f}`);
 // Covers static imports, dynamic imports and Vite's rewritten chunk references.
 if(f.endsWith('.js'))for(const match of bytes.toString().matchAll(/["'](\.\.?\/[^"']+\.(?:js|css))["']/g))assert.ok(existsSync(resolve(dirname(`dist/${f}`),match[1])),`Broken import in ${f}: ${match[1]}`);
}
const pkg=JSON.parse(readFileSync('package.json')),lock=JSON.parse(readFileSync('package-lock.json'));
assert.equal(pkg.version,lock.version);assert.equal(pkg.version,lock.packages[''].version);
for(const kind of ['dependencies','devDependencies']){
 assert.deepEqual(pkg[kind],lock.packages[''][kind],`Lockfile ${kind}`);
 for(const [name,version] of Object.entries(pkg[kind]||{})){
  assert.match(version,/^\d+\.\d+\.\d+$/,`Dependency must be pinned: ${name}`);
  assert.equal(lock.packages[`node_modules/${name}`]?.version,version,`Locked version ${name}`);
 }
}
assert.match(pkg.devDependencies.vite,/^8\./,'Supported Vite 8 toolchain');
assert.ok(pkg.scripts.typecheck.includes('tsc'),'Separate TypeScript check');
const html=readFileSync('dist/index.html','utf8');
assert.ok(!html.includes('catalog-expanded'),'Hub must not load catalog');
const registry=JSON.parse(readFileSync('dist/publication.json','utf8'));
for(const c of registry.cases){
 const report=readFileSync(`dist/reports/${c.reportId}_Review.html`,'utf8');
 assert.ok(report.includes(`id="${c.sectionId}"`),'Missing stable return section');
 assert.equal(c.entryURL,new URL(`cases/${c.caseId}/v${c.caseVersion}/`,deploy.PUBLIC_BASE_URL).href);
}
const build=html.match(/name="app-build" content="([^"]+)"/)?.[1];
assert.ok(build,'Missing build identity');
assert.ok(html.includes(`name="app-base-path" content="${deploy.BASE_PATH}"`),'Wrong runtime base path');
assert.match(html, /name="robots" content="noindex,nofollow"/);
// Validate all local HTML links, including report return links and graph alternatives.
for(const file of files.filter(path=>path.endsWith('.html'))){
 const text=readFileSync(`dist/${file}`,'utf8');
 const base=new URL(file,deploy.PUBLIC_BASE_URL);
 for(const match of text.matchAll(/(?:src|href)="([^"]+)"/g)){
  const raw=match[1];
  if(raw.startsWith('#')||/^(?:https?:|data:|mailto:)/.test(raw))continue;
  const target=new URL(raw,base);
  assert.equal(target.origin,new URL(deploy.PUBLIC_BASE_URL).origin,`Unexpected local origin in ${file}`);
  assert.ok(target.pathname.startsWith(deploy.BASE_PATH),`Link outside deployment path in ${file}: ${raw}`);
  const relative=decodeURIComponent(target.pathname.slice(deploy.BASE_PATH.length))||'index.html';
  assert.ok(existsSync(resolve('dist',relative)),`Broken local HTML resource in ${file}: ${raw}`);
 }
}
console.log(JSON.stringify({status:'PASS',build,version:pkg.version,node:process.version,...deploy,files:files.map(path=>({path,bytes:readFileSync(`dist/${path}`).length,sha256:sha(readFileSync(`dist/${path}`))}))},null,2));
