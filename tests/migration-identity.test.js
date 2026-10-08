import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {products} from '../data.js';
import {normalizeScience, createProject, exportProject, importProject} from '../science.js';

test('migration keeps legacy project import with SKU, quantity, text and document references', () => {
  const science = normalizeScience();
  const project = createProject(science, {name:'Сумісний проєкт', candidates:['u02','c04']}, products, '2026-10-08T12:00:00.000Z');
  project.note = 'Перенесення між адресами виконується лише через файл.';
  project.quantities = {u02:3,c04:2};
  project.chosen = ['u02','c04'];
  project.references = [{title:'D1',url:'#/ng/document/u02',productId:'u02'}];
  const payload = exportProject(project);
  assert.equal(JSON.parse(payload).format,'perspektyva-project');
  assert.deepEqual(importProject(payload,Buffer.byteLength(payload)),project);
});

test('current public identity is consistent and does not fetch third-party fonts', () => {
  const index = readFileSync(new URL('../index.html',import.meta.url),'utf8');
  const app = readFileSync(new URL('../app.js',import.meta.url),'utf8');
  assert.match(index, /ASP24 \/ NG Group — Demo &amp; Research/);
  assert.doesNotMatch(index,/fonts\.googleapis|fonts\.gstatic|rel="preconnect"/);
  assert.doesNotMatch(app,/Перспектив|Perspektyva-/);
  assert.match(app,/Не вводьте особистих даних/);
  assert.equal(JSON.parse(readFileSync(new URL('../package.json',import.meta.url))).name,'asp24-nggroup-demo-research');
});
