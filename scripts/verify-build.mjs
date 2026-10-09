/** Verify deploy contents, module references and exact approved reports. No network required. */
import {readdirSync,readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import assert from 'node:assert/strict';
import {normalizeBasePath} from './deployment-config.mjs';
const walk=(dir,base='')=>readdirSync(dir,{withFileTypes:true}).flatMap(x=>x.isDirectory()?walk(`${dir}/${x.name}`,`${base}${x.name}/`):[`${base}${x.name}`]).sort();
const publicFiles=['assets/asp24-original.webp','assets/ng-original.svg','design-tokens.css','favicon.svg','reports/ASP24_Review.pdf','reports/NGGroup_Review.pdf',...JSON.parse(readFileSync('reports/html-public-assets.json','utf8'))].sort();
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
const generated=/^assets\/(app|asset-url|data|catalog-expanded|validation|logic|orders|presentation|catalog-ui|science|scenarios|lab|style|finish|catalog)-[a-f0-9]{12}\.(js|css)$/;
assert.deepEqual(files.filter(p=>!['index.html','build-config.json'].includes(p)&&!generated.test(p)),publicFiles,'Unexpected deployed file');
for(const name of ['app','asset-url','data','catalog-expanded','validation','logic','orders','presentation','catalog-ui','science','scenarios','lab'])assert.equal(files.filter(p=>new RegExp(`^assets/${name}-[a-f0-9]{12}\\.js$`).test(p)).length,1,`Module ${name}`);
for(const name of ['style','finish','catalog','science'])assert.equal(files.filter(p=>new RegExp(`^assets/${name}-[a-f0-9]{12}\\.css$`).test(p)).length,1,`Stylesheet ${name}`);
for(const f of publicFiles)assert.equal(sha(readFileSync(`public/${f}`)),sha(readFileSync(`dist/${f}`)),f);
for(const [f,hash]of Object.entries(expectedPDFs)){const pdf=readFileSync(`dist/reports/${f}`);assert.equal(pdf.subarray(0,5).toString(),'%PDF-',f);assert.equal(sha(pdf),hash,f);}
for(const f of files.filter(x=>generated.test(x))){
 const bytes=readFileSync(`dist/${f}`); assert.ok(f.includes(sha(bytes).slice(0,12)),`Fingerprint ${f}`);
 if(f.endsWith('.js'))for(const match of bytes.toString().matchAll(/\bfrom\s*['"](\.[^'"]+)['"]/g))assert.ok(existsSync(resolve(dirname(`dist/${f}`),match[1])),`Broken import in ${f}`);
}
const pkg=JSON.parse(readFileSync('package.json')),lock=JSON.parse(readFileSync('package-lock.json'));
assert.equal(pkg.version,lock.version);assert.equal(pkg.version,lock.packages[''].version);
assert.equal(Object.keys(pkg.dependencies||{}).length,0);assert.equal(Object.keys(pkg.devDependencies||{}).length,0);
const html=readFileSync('dist/index.html','utf8');
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
