import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, cpSync, readdirSync, readFileSync, writeFileSync, rmSync, mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync, spawn} from 'node:child_process';
import {createServer} from 'node:net';
import {assetUrl} from '../asset-url.js';
import {getDeploymentConfig} from '../scripts/deployment-config.mjs';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

test('deployment config derives matching URL and prefix and rejects ambiguous targets', () => {
  const defaults = getDeploymentConfig({});
  assert.equal(new URL(defaults.PUBLIC_BASE_URL).pathname, defaults.BASE_PATH);
  assert.equal(getDeploymentConfig({BASE_PATH:'/'}).BASE_PATH, '/');
  assert.equal(new URL(getDeploymentConfig({BASE_PATH:'/'}).PUBLIC_BASE_URL).pathname, '/');
  assert.equal(getDeploymentConfig({PUBLIC_BASE_URL:'https://example.org/demo/'}).BASE_PATH, '/demo/');
  assert.throws(() => getDeploymentConfig({PUBLIC_BASE_URL:'https://example.org/demo/', BASE_PATH:'/other/'}), /disagree/);
  for (const value of ['//other/', '/../', '/a/../../', 'https://other/', '/a?x/']) assert.throws(() => getDeploymentConfig({BASE_PATH:value}));
});

test('asset paths preserve project directory and reject traversal or remote URLs', () => {
  for (const base of ['/', '/asp24-nggroup-demo-research/']) {
    assert.equal(assetUrl('assets/mini-ups.webp', base), `${base}assets/mini-ups.webp`);
    assert.equal(assetUrl('/reports/ASP24_Review.pdf', base), `${base}reports/ASP24_Review.pdf`);
    for (const path of ['../secret', '//other/file', 'https://other/file', 'assets/../secret', 'assets\\bad', 'file?q=1']) assert.throws(() => assetUrl(path, base));
  }
});

function snapshot() {
  const dir = mkdtempSync(join(tmpdir(), 'asp24-pages-test-'));
  for (const entry of readdirSync(root)) {
    if (/\.(js|css)$/.test(entry) || ['index.html','deployment.config.json','package.json','package-lock.json'].includes(entry)) cpSync(join(root,entry),join(dir,entry));
  }
  cpSync(join(root,'public'),join(dir,'public'),{recursive:true});
  mkdirSync(join(dir,'scripts')); mkdirSync(join(dir,'reports'));
  for (const name of ['build-static.mjs','verify-build.mjs','deployment-config.mjs','serve.mjs']) cpSync(join(root,'scripts',name),join(dir,'scripts',name));
  for (const name of ['content.json','pdf-manifest.json','html-manifest.json','html-public-assets.json']) cpSync(join(root,'reports',name),join(dir,'reports',name));
  const inputs=JSON.parse(readFileSync(join(root,'reports/input-manifest.json'),'utf8'));
  for(const name of ['reports/input-manifest.json',...Object.keys(inputs.files)]) {
    mkdirSync(dirname(join(dir,name)),{recursive:true});cpSync(join(root,name),join(dir,name));
  }
  return dir;
}
async function freePort() {
  const server = createServer();
  await new Promise((resolve,reject) => {server.once('error',reject); server.listen(0,'127.0.0.1',resolve);});
  const port = server.address().port;
  await new Promise(resolve => server.close(resolve));
  return port;
}

for (const base of ['/', '/asp24-nggroup-demo-research/']) {
  test(`real HTTP preview serves exact build at ${base}`, async () => {
    const dir = snapshot();
    let server;
    try {
      const env = {...process.env, BASE_PATH:base};
      delete env.PUBLIC_BASE_URL;
      execFileSync(process.execPath,['scripts/build-static.mjs'],{cwd:dir,env});
      const verified = JSON.parse(execFileSync(process.execPath,['scripts/verify-build.mjs'],{cwd:dir,env,encoding:'utf8'}));
      assert.equal(verified.status,'PASS');
      assert.equal(verified.BASE_PATH,base);
      // A matching PDF byte hash cannot make an outdated report source acceptable.
      const manifestPath=join(dir,'reports/pdf-manifest.json');
      const manifestText=readFileSync(manifestPath,'utf8');
      const stale=JSON.parse(manifestText); stale[0].content_sha256='0'.repeat(64);
      writeFileSync(manifestPath,JSON.stringify(stale));
      assert.throws(()=>execFileSync(process.execPath,['scripts/verify-build.mjs'],{cwd:dir,env,stdio:'pipe'}), /PDF built from outdated content/);
      writeFileSync(manifestPath,manifestText);

      const port = await freePort();
      server = spawn(process.execPath,['scripts/serve.mjs','--port',String(port)],{cwd:dir,stdio:['ignore','pipe','pipe']});
      await new Promise((resolve,reject) => {
        const timer = setTimeout(()=>reject(new Error('Preview startup timed out')),5000);
        server.once('error',reject);
        server.once('exit',code=>reject(new Error(`Preview exited ${code}`)));
        server.stdout.on('data',chunk=>{if(String(chunk).includes('Preview:')){clearTimeout(timer);resolve();}});
      });
      const origin = `http://127.0.0.1:${port}`;
      for (const file of verified.files) {
        const response = await fetch(origin + base + file.path);
        assert.equal(response.status,200,file.path);
        assert.deepEqual(Buffer.from(await response.arrayBuffer()),readFileSync(join(dir,'dist',file.path)),file.path);
      }
      const index = await fetch(origin+base+'#/asp/compare');
      assert.equal(index.status,200);
      const text = await index.text();
      assert.ok(text.includes(`name="app-base-path" content="${base}"`));
      assert.equal((await fetch(origin+base+'reports/ASP24_Review.pdf')).headers.get('content-type'),'application/pdf');
      assert.equal((await fetch(origin+base+'reports/NGGroup_Review.html')).headers.get('content-type'),'text/html; charset=utf-8');
      assert.equal((await fetch(origin+base+'package.json')).status,404);
      for (const excluded of ['mini-ups','network-cable','network-switch','optical-transceiver']) assert.equal((await fetch(origin+base+`assets/${excluded}.webp`)).status,404);
      assert.equal((await fetch(origin+base+'index.html',{method:'POST'})).status,405);
      if (base !== '/') {
        assert.equal((await fetch(origin+'/reports/ASP24_Review.pdf')).status,404);
        assert.equal((await fetch(origin+'/assets/mini-ups.webp')).status,404);
        const redirect=await fetch(origin+base.slice(0,-1),{redirect:'manual'});
        assert.equal(redirect.status,308); assert.equal(redirect.headers.get('location'),base);
      }
    } finally {
      if (server && server.exitCode === null) {
        server.kill();
        await new Promise(resolve=>server.once('exit',resolve));
      }
      rmSync(dir,{recursive:true,force:true});
    }
  });
}


test('publication verifier limits both initial URLs and redirects to the exact project', () => {
  const script = `import importlib.util, urllib.request, urllib.error
spec = importlib.util.spec_from_file_location('publication', 'scripts/verify-published.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
base = 'https://mathewfromua.github.io/asp24-nggroup-demo-research/'
prefix = '/asp24-nggroup-demo-research/'
assert m.allowed_url(base + 'reports/ASP24_Review.pdf', prefix)
for value in ['https://mathewfromua.github.io/another-project/file', 'https://mathewfromua.github.io.evil.example/asp24-nggroup-demo-research/file', base + '../secret', base + '%2e%2e/secret', 'http://mathewfromua.github.io' + prefix, base + '?token=no']:
    assert not m.allowed_url(value, prefix), value
handler = m.AuthorizedRedirect(base)
request = urllib.request.Request(base)
assert handler.redirect_request(request, None, 302, 'Found', {}, base + 'index.html').full_url == base + 'index.html'
for value in ['https://example.org/', 'https://mathewfromua.github.io/other/', base + '../other/']:
    try:
        handler.redirect_request(request, None, 302, 'Found', {}, value)
    except urllib.error.URLError:
        pass
    else:
        raise AssertionError('Unsafe redirect accepted')
print('PASS')
`;
  assert.equal(execFileSync('python3',['-B','-c',script],{cwd:root,encoding:'utf8'}).trim(),'PASS');
});
