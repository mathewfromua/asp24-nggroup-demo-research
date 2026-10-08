import test from 'node:test';
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import { products } from '../data.js';
import { SCIENCE_LIMITS,normalizeScience,createProject,duplicateProject,validateProject,exportProject,importProject,projectCart,projectText,renderScience,handleScience,safeReferenceUrl,modelMapQuery } from '../science.js';
import { labNotes,renderConnectorAtlas } from '../lab.js';
const now='2026-10-07T12:00:00.000Z';
const create=(science,name='A',ids=['u02','c02'])=>createProject(science,{name,candidates:ids},products,now);
test('independent projects, duplicate references and quantities do not alias or mutate cart',()=>{
 const science=normalizeScience(),a=create(science),b=create(science,'B',['u01']);a.chosen=['u02'];a.quantities.u02=3;a.references.push({title:'D1',url:'#/ng/document/u02',productId:'u02'});
 const copy=duplicateProject(science,a.id,products,now);copy.quantities.u02=9;copy.references[0].title='Copy';copy.chosen=[];
 assert.equal(a.quantities.u02,3);assert.equal(a.references[0].title,'D1');assert.deepEqual(a.chosen,['u02']);assert.deepEqual(b.candidates,['u01']);assert.notEqual(copy.id,a.id);assert.equal(science.projects.length,3);
});
test('project quantities preserve exact cable units and amounts, cart uses chosen IDs only',()=>{
 const science=normalizeScience(),p=create(science,'Cable',['u02','c02','c04']);p.chosen=['u02','c02','c04'];p.quantities={u02:3,c02:2,c04:2};
 const cart=projectCart(p);assert.deepEqual(cart,{u02:3,c02:2,c04:2});
 assert.equal(products.find(x=>x.id==='u02').price*cart.u02,657000);
 assert.equal(products.find(x=>x.id==='c02').price*cart.c02,518000);
 assert.equal(products.find(x=>x.id==='c04').price*cart.c04,1038000);
 const text=projectText(p);assert.match(text,/200 м/);assert.match(text,/610 м/);
});
test('export/import round trip, stable IDs, HTML inert in rendering',()=>{
 const science=normalizeScience(),p=create(science,'<img src=x onerror=alert(1)>');p.note='<script>alert(1)</script>';p.quantities.u02=3;p.chosen=['u02'];
 const text=exportProject(p),restored=importProject(text,new TextEncoder().encode(text).length);assert.deepEqual(restored,p);
 const html=renderScience({page:'project',id:p.id,params:new URLSearchParams()}, {science},'asp');assert.ok(html.includes('&lt;img'));assert.ok(html.includes('&lt;script&gt;'));assert.ok(!html.includes('<script>alert'));
});
test('JSON import rejects size, version, ID, types, numeric range, unsafe keys and unsafe URL',()=>{
 const science=normalizeScience(),p=create(science),base=JSON.parse(exportProject(p));
 const reject=patch=>{const value=structuredClone(base);patch(value);const text=JSON.stringify(value);assert.throws(()=>importProject(text,new TextEncoder().encode(text).length));};
 reject(v=>v.version=2);reject(v=>v.project.candidates.push('unknown'));reject(v=>v.project.quantities.u02='3');reject(v=>v.project.quantities.u02=1000);reject(v=>v.project.chosen=['u01']);reject(v=>v.project.name='');reject(v=>v.project.references=[{title:'X',url:'javascript:alert(1)'}]);reject(v=>v.project.references=[{title:'X',url:'https://user:pass@example.com/'}]);reject(v=>v.project.quantities.constructor=2);
 assert.throws(()=>importProject('{"format":"perspektyva-project","version":1,"__proto__":{}}',100));assert.throws(()=>importProject(exportProject(p),SCIENCE_LIMITS.importBytes+1));assert.throws(()=>importProject('x'.repeat(SCIENCE_LIMITS.importBytes+1),1));
 assert.equal(safeReferenceUrl('#/ng/document/u02'),true);assert.equal(safeReferenceUrl('#/ng/document/constructor'),false);
});
test('invalid stored projects quarantined with raw values; valid projects survive reload',()=>{
 const science=normalizeScience(),p=create(science);const bad=structuredClone(p);bad.id='project-77';bad.quantities.u02=-1;
 const restored=normalizeScience({...science,projects:[p,bad]});assert.equal(restored.projects.length,1);assert.equal(restored.quarantine.length,1);assert.deepEqual(restored.quarantine[0].raw,bad);assert.deepEqual(normalizeScience(restored),restored);
 assert.equal(normalizeScience({version:7,projects:[p]}).quarantine.length,1);assert.equal(normalizeScience({...science,projects:[p,p]}).quarantine.length,1);
});
test('unavailable selection blocks transfer, explicit add/replace invokes helper, template leaves cart intact',()=>{
 const state={science:normalizeScience(),cart:{u01:2}},messages=[],calls=[];const h={save:()=>true,render:()=>{},toast:t=>messages.push(t),go:()=>{},openModal:()=>{},closeModal:()=>{},downloadText:()=>{},setComparison:()=>true,transferCart:(items,mode)=>{calls.push({items,mode});return true;}};
 handleScience('science-template',{id:'quiet-office'},state,h);assert.equal(state.science.projects.length,1);assert.deepEqual(state.cart,{u01:2});assert.equal(calls.length,0);
 const p=create(state.science,'Transfer',['u02','u03']);p.chosen=['u02'];p.quantities.u02=3;handleScience('science-cart',{project:p.id},state,h);assert.equal(calls.length,0);
 handleScience('science-transfer',{project:p.id,mode:'add'},state,h);handleScience('science-transfer',{project:p.id,mode:'replace'},state,h);assert.deepEqual(calls,[{items:{u02:3},mode:'add'},{items:{u02:3},mode:'replace'}]);p.chosen=['u03'];assert.throws(()=>projectCart(p));
});
test('comparison save captures candidates without changing chosen/cart; explicit >6 selection validates',()=>{
 const state={science:normalizeScience(),cart:{u02:3}},calls=[],h={save:()=>true,render:()=>{},toast:()=>{},go:()=>{},openModal:()=>{},closeModal:()=>{},downloadText:()=>{},setComparison:(ids,group)=>calls.push({ids,group}),transferCart:()=>{throw Error('Unexpected cart action');}};
 handleScience('comparison-save-to-project',{ids:['u01','u02'],target:'new'},state,h);const p=state.science.projects[0];assert.deepEqual(p.candidates,['u01','u02']);assert.deepEqual(p.chosen,[]);assert.deepEqual(state.cart,{u02:3});
 handleScience('science-submit',{form:'compare-selection',project:p.id,group:'ups',ids:['u01','u02'],values:{}},state,h);assert.deepEqual(calls,[{ids:['u01','u02'],group:'ups'}]);
 handleScience('science-submit',{form:'compare-selection',project:p.id,group:'constructor',ids:['u01'],values:{}},state,h);assert.equal(calls.length,1);
});
test('12 short sourced lab notes and connector atlas are complete; map unknowns separated',()=>{
 assert.deepEqual(labNotes.map(({id,group,example,source})=>({id,group,example,source})),JSON.parse(readFileSync(new URL('./lab-note-contract.json',import.meta.url))));
 assert.equal(labNotes.length,12);for(const n of labNotes){assert.ok(n.text.trim());assert.ok(n.text.trim().split(/\s+/).length<=120);assert.ok(n.question&&n.example&&n.group&&n.source.url.startsWith('https://'));}
 const atlas=renderConnectorAtlas();assert.equal((atlas.match(/<svg/g)||[]).length,5);assert.ok(atlas.includes('<title'));
 const map=renderScience({page:'model-map',params:new URLSearchParams('cat=ups&facet=massG')},{science:normalizeScience()},'asp');assert.ok(map.includes('<table'));assert.ok(map.includes('Поза графіком'));assert.ok(map.includes('#/asp/product/u02'));assert.ok(!map.includes('NaN'));
});
test('storage refusal is explicit and project can still be exported from memory',()=>{
 const state={science:normalizeScience()},messages=[],h={save:()=>false,render:()=>{},toast:t=>messages.push(t),go:()=>{},openModal:()=>{},closeModal:()=>{},downloadText:()=>{}};
 handleScience('science-create',{},state,h);assert.equal(state.science.projects.length,1);assert.match(messages[0],/лише в пам’яті/);assert.ok(exportProject(state.science.projects[0]));
});
test('model map keeps catalog query and facets on Y change; category change clears only incompatible filters',()=>{
 const query='cat=ups&q=VOLTYN&f0=36+Вт&f0=60+Вт&n_energyWh_min=60&available=1&sort=energyWh-down&view=list&facet=energyWh';
 const changed=modelMapQuery(query,{cat:'ups',facet:'massG'});assert.equal(changed.get('q'),'VOLTYN');assert.deepEqual(changed.getAll('f0'),['36 Вт','60 Вт']);assert.equal(changed.get('n_energyWh_min'),'60');assert.equal(changed.get('facet'),'massG');
 const next=modelMapQuery(query,{cat:'optics'});assert.equal(next.get('q'),'VOLTYN');assert.equal(next.get('available'),'1');assert.equal(next.get('view'),'list');assert.equal(next.has('f0'),false);assert.equal(next.has('n_energyWh_min'),false);assert.equal(next.has('sort'),false);assert.equal(next.has('facet'),false);
 const html=renderScience({page:'model-map',params:new URLSearchParams('cat=ups&q=DEMO-U02')},{science:normalizeScience()},'asp');assert.match(html,/1 модель за обраними умовами/);assert.ok(!html.includes('#/asp/product/u01'));
});
test('empty legacy science state is not quarantined; map Enter works without a project and modal has labelled heading',()=>{
 assert.equal(normalizeScience({}).quarantine.length,0);
 const state={science:normalizeScience()},events=[],h={save:()=>true,render:()=>{},toast:t=>events.push(t),go:url=>events.push(url),openModal:html=>events.push(html),closeModal:()=>{}};
 handleScience('science-submit',{form:'map',query:'cat=ups&available=1',values:{cat:'ups',facet:'energyWh'}},state,h);assert.equal(events[0],'#/asp/model-map?cat=ups&available=1&facet=energyWh');
 handleScience('comparison-save-to-project',{ids:['u02']},state,h);assert.match(events[1],/<h2 id="dialog-title">/);
});
test('map plots actual nested numericFacet values and separates only genuinely unknown values',()=>{
 const rendered=(query)=>renderScience({page:'model-map',params:new URLSearchParams(query)},{science:normalizeScience()},'asp');
 const energy=rendered('cat=ups&facet=energyWh');assert.equal((energy.match(/class="science-map-point[^"]*"/g)||[]).length,48);assert.ok(!energy.includes('Поза графіком'));assert.ok(!energy.includes('NaN'));
 const filtered=rendered('cat=ups&q=VOLTYN&f0=36+Вт&available=1&facet=energyWh');assert.equal((filtered.match(/class="science-map-point[^"]*"/g)||[]).length,2);
 const mass=rendered('cat=ups&facet=massG');assert.equal((mass.match(/class="science-map-point[^"]*"/g)||[]).length,products.filter(p=>p.group==='ups'&&p.numericFacets.massG.value!==null).length);assert.match(mass,/Поза графіком: 7 моделей/);assert.ok(mass.includes('cy="'));
});
test('NG projects and templates route commercial-only models to same-ID ASP24 cards',()=>{
 const science=normalizeScience(),p=create(science,'NG selection',['u02','s01','c03']);
 const html=renderScience({page:'project',id:p.id,params:new URLSearchParams()},{science},'ng');assert.ok(html.includes('href="#/asp/product/s01"'));assert.ok(html.includes('href="#/asp/product/c03"'));assert.ok(html.includes('href="#/ng/product/u02"'));assert.ok(!html.includes('href="#/ng/product/s01"'));assert.ok(!html.includes('href="#/ng/product/c03"'));assert.ok(html.includes('science-brand-label">ASP24'));
 const templates=renderScience({page:'templates',params:new URLSearchParams()},{science},'ng');assert.ok(templates.includes('href="#/asp/product/s01"'));assert.ok(!templates.includes('href="#/ng/product/s01"'));assert.ok(templates.includes('science-brand-label">ASP24'));
});
