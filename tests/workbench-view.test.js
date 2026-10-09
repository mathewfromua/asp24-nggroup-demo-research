import test from 'node:test';
import assert from 'node:assert/strict';
import {initialState, migrateState} from '../logic.js';

const route = '#/asp/compare?experience=modern';
test('schema 4 retains bounded workbench reading context without changing six candidates, pair or private work', () => {
  const source = initialState();
  source.compareByGroup.ups = ['u01','u02','u03','u04','u05','u06'];
  source.view.pairs.ups = ['u05','u06'];
  source.cart = {u02:3};
  source.drafts.u02 = {purpose:'Тест',quantity:'2',question:'  D1\nТочне питання  '};
  const modern = {group:'ups',pairFocus:true,full:{x:82,y:210},pair:{x:0,y:206}};
  source.view.pages[route] = {scroll:491,details:[false],focus:'[data-wb-focus="model-pair-u05"]',modern};
  const restored = migrateState(JSON.parse(JSON.stringify(source)));
  assert.equal(restored.version,4);
  assert.deepEqual(restored.view.pages[route],source.view.pages[route]);
  for(const field of ['compareByGroup','cart','drafts']) assert.deepEqual(restored[field],source[field]);
  assert.deepEqual(restored.view.pairs.ups,source.view.pairs.ups);
  assert.deepEqual(migrateState(restored).view.pages[route].modern,modern);
});

test('untrusted workbench presentation cannot inject a category, nonfinite geometry or executable values', () => {
  const pages = {
    [route]: {modern:{group:'ups',pairFocus:'true',full:{x:-1,y:Infinity},pair:{x:10001,y:1e9},extra:'ignored'}},
    '#/ng/compare?experience=modern': {modern:{group:'constructor',pairFocus:true,full:{x:1,y:2}}},
    '#/asp/compare': {modern:{group:'ups',pairFocus:true}},
    '#/asp/product/u02': {modern:{group:'ups',pairFocus:true}},
    'javascript:alert(1)': {modern:{group:'ups',pairFocus:true}},
  };
  const result = migrateState({view:{pages}});
  assert.deepEqual(result.view.pages[route].modern,{group:'ups',pairFocus:false,full:{x:0,y:0},pair:{x:10000,y:100000}});
  for(const url of Object.keys(pages).slice(1,4)) assert.equal(result.view.pages[url].modern,undefined);
  assert.equal(result.view.pages['javascript:alert(1)'],undefined);
  const legacy = migrateState({version:4,view:{pages:{[route]:{scroll:12,details:[true],focus:'#main'}}}});
  assert.equal(legacy.view.pages[route].modern,undefined);
  assert.deepEqual(migrateState({view:{pages:{[route]:{modern:{group:'ups',full:{x:'12',y:NaN},pair:['invalid']}}}}}).view.pages[route].modern,
    {group:'ups',pairFocus:false,full:{x:0,y:0},pair:{x:0,y:0}});
});
