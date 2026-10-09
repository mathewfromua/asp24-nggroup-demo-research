import test from 'node:test';
import assert from 'node:assert/strict';
import {products as legacyProducts, groups as legacyGroups} from '../data.js';
import * as legacyLogic from '../logic.js';
import * as comparison from '../src/domain/comparison.ts';
import {products, groups, validateCatalog, validateGroups, parseCatalogJson} from '../src/data/catalog.ts';
import {filterProducts} from '../src/domain/catalog.ts';
import {initialState, migrateState} from '../src/domain/state.ts';
import {readState, writeState} from '../src/adapters/storage.ts';
import {createProject, normalizeScience, mergeProjectCandidates, projectText} from '../src/domain/projects.ts';
import {exportProject, importProject} from '../src/adapters/project-json.ts';
import * as legacyScience from '../science.js';

const fixture = props => ({...products[0], props});
const selected = () => {const state=initialState(); for(const p of products.filter(p=>p.group==='ups').slice(0,6)) comparison.addComparison(state,p.id);return state;};

test('typed domain and legacy UI share exact function and catalog instances', () => {
  assert.equal(legacyLogic.addComparison, comparison.addComparison);
  assert.equal(legacyLogic.filterProducts, filterProducts);
  assert.equal(legacyLogic.readState, readState);
  assert.equal(legacyScience.createProject, createProject);
  assert.equal(legacyScience.importProject, importProject);
  assert.equal(products,legacyProducts);assert.equal(groups,legacyGroups);
  assert.equal(products.length,384);assert.equal(Object.keys(groups).length,8);assert.equal(new Set(products.map(p=>p.manufacturer)).size,13);
});

test('parameter states retain zero, false, unknown, missing, inapplicable and conflict without inventing equality', () => {
  const key='Потужність';
  const models=[fixture({[key]:0}),fixture({[key]:false}),fixture({[key]:null}),fixture({}),fixture({[key]:{status:'not-applicable',reason:'Немає цього інтерфейсу'}}),fixture({[key]:{status:'conflicting',values:[{status:'known',value:1,unit:'W'},{status:'known',value:2,unit:'W'}]}})].map((p,i)=>({...p,id:`test${i}`}));
  const row=comparison.comparisonRows(models).find(row=>row.key===key);
  assert.deepEqual(row.cells.map(cell=>cell.value.status),['known','known','unknown','missing','not-applicable','conflicting']);
  assert.equal(row.cells[0].text,'0');assert.equal(row.cells[1].text,'false');
  assert.match(row.cells[2].text,/Не уточнено/);assert.match(row.cells[3].text,/відсутній/);assert.match(row.cells[4].text,/Не застосовується/);assert.match(row.cells[5].text,/1 W \/ 2 W/);
  assert.equal(row.different,true);assert.equal(row.incomplete,true);assert.equal(row.conflicting,true);
  assert.equal(comparison.comparisonRows([models[0],models[2]])[0].different,false);
  assert.equal(comparison.comparisonRows([models[0],models[4]])[0].different,true);
  assert.deepEqual(comparison.comparisonRows([products[0],products.find(p=>p.group==='optics')]),[]);
  assert.deepEqual(comparison.comparisonKeys([products[0],products.find(p=>p.group==='optics')]),[]);
  const formatted=[fixture({[key]:{status:'known',value:1000,unit:'W'}}),fixture({[key]:'1 000 W'})];
  assert.equal(comparison.comparisonStatus(formatted,key).different,false);
});

test('runtime catalog boundary rejects duplicate IDs, unknown schema and invalid units or values', () => {
  validateCatalog(products);validateGroups(groups);
  assert.throws(()=>validateGroups({...groups,unexpected:{}}));
  const encode=ps=>JSON.stringify({schemaVersion:1,sourceKind:'synthetic-ui-fixture',products:ps});
  assert.deepEqual(parseCatalogJson(encode(products)),products);
  assert.throws(()=>parseCatalogJson(JSON.stringify({schemaVersion:4,products})),/schemaVersion 1/);
  assert.throws(()=>parseCatalogJson(encode([products[0],products[0]])),/stable ID/);
  assert.throws(()=>validateCatalog([{...products[0],price:1.5}]),/ціна/);
  assert.throws(()=>validateCatalog([{...products[0],props:{power:{status:'known',value:NaN}}}]),/параметри/);
  const cable=products.find(p=>p.group==='cable');
  assert.throws(()=>validateCatalog([{...cable,unitDefinition:{kind:'reel',integerOnly:true,lengthM:0}}]),/одиниця/);
  // Similar name or reused vendor SKU never merges distinct stable IDs.
  const other={...products[0],id:'externalsame',revision:'D2'};
  assert.equal(parseCatalogJson(encode([products[0],other])).length,2);
});

test('typed recovery retains six IDs, active pair, exact draft and legacy project after reload', () => {
  const state=selected();state.view.pairs.ups=[state.compareByGroup.ups[5],state.compareByGroup.ups[0]];
  state.drafts.u01={purpose:'Тест',quantity:'2',question:'  Точний текст\n0 ≠ unknown  '};
  state.science=normalizeScience(null);const project=createProject(state.science,{name:'Legacy JSON',candidates:['u01']});
  const oldJson=legacyScience.exportProject(project);assert.equal(oldJson,exportProject(project));
  assert.deepEqual(importProject(oldJson,Buffer.byteLength(oldJson)),project);
  let bytes=null;const storage={getItem:()=>bytes,setItem:(_key,value)=>{bytes=value;}};
  assert.equal(writeState(storage,state),true);const restored=readState(storage).state;
  assert.deepEqual(restored.compareByGroup,state.compareByGroup);assert.deepEqual(restored.view.pairs,state.view.pairs);
  assert.deepEqual(restored.drafts,state.drafts);assert.deepEqual(restored.science,state.science);
  const token=comparison.removeComparison(restored,restored.compareByGroup.ups[0]);
  assert.equal(comparison.undoComparison(restored,token),true);assert.deepEqual(restored.compareByGroup,state.compareByGroup);
  const denied={getItem:()=>{throw new Error('denied');},setItem:()=>{throw new Error('must not overwrite');}};
  assert.equal(readState(denied).status,'denied');assert.equal(writeState(denied,state),false);
  const corrupt=readState({getItem:()=>'{corrupt',setItem:()=>{}});
  assert.equal(corrupt.status,'corrupt');assert.equal(corrupt.state.recovery.rawState,'{corrupt');
  assert.equal(migrateState({version:1,compare:['u01','u02']}).version,4);
});

test('project limit is atomic at 64; unknown cable length never becomes a claimed zero metres', () => {
  const science=normalizeScience(null),ids=products.slice(0,64).map(p=>p.id);
  const project=createProject(science,{candidates:ids});const before=structuredClone(project);
  assert.throws(()=>mergeProjectCandidates(project,[products[64].id]),/64 кандидатів/);assert.deepEqual(project,before);
  const cable=products.find(p=>p.group==='cable');const uncertain={...cable,unit:'бухта',unitDefinition:undefined};
  const cableProject=createProject(normalizeScience(null),{candidates:[cable.id]});
  const text=projectText(cableProject,[uncertain]);assert.match(text,/Метраж не уточнено/);assert.doesNotMatch(text,/· 0 м/);
});
