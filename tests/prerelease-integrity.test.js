import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import {products, byId} from '../data.js';
import {comparisonStatus, comparisonKeys, semantic, listText, consultationText, initialState, STATE_KEY} from '../logic.js';
import {normalizeScience, createProject, duplicateProject, importProject, exportProject, handleScience, mergeProjectCandidates} from '../science.js';
import {renderCatalog} from '../catalog-ui.js';

const ids=products.slice(0,65).map(p=>p.id);
const now='2026-10-09T00:00:00.000Z';
const create=(s,count)=>createProject(s,{name:'Boundary',candidates:ids.slice(0,count)},products,now);
const snapshot=s=>JSON.stringify(s);
function helpers(){const calls={saves:0,messages:[]};return {calls,save(){calls.saves++;return true;},render(){},toast(t){calls.messages.push(t);},go(){},openModal(){},closeModal(){}};}

test('project limit: 63→64, repeated add, 65th add and batch merge are atomic',()=>{
 const state={science:normalizeScience()},p=create(state.science,63),h=helpers();
 handleScience('science-add-candidate',{project:p.id,id:ids[63]},state,h);
 assert.equal(p.candidates.length,64);assert.equal(p.quantities[ids[63]],1);assert.equal(h.calls.saves,1);
 const before=snapshot(state);
 for(const id of [ids[63],ids[64]])handleScience('science-add-candidate',{project:p.id,id},state,h);
 assert.equal(snapshot(state),before);assert.equal(h.calls.saves,1);assert.match(h.calls.messages.at(-1),/64/);
 const other={science:normalizeScience()},target=create(other.science,63),otherHelpers=helpers(),original=snapshot(other);
 handleScience('comparison-save-to-project',{target:target.id,ids:[ids[62],ids[63],ids[64]]},other,otherHelpers);
 assert.equal(snapshot(other),original);assert.equal(otherHelpers.calls.saves,0);assert.match(otherHelpers.calls.messages.at(-1),/64/);
 mergeProjectCandidates(target,[ids[62],ids[63]]);assert.equal(target.candidates.length,64);
 assert.deepEqual(normalizeScience(other.science),other.science);
});

test('64 candidates duplicate, legacy import and reload losslessly; 65 reject before state or sequence changes',()=>{
 const science=normalizeScience(),p=create(science,64);p.chosen=[ids[2]];p.quantities[ids[2]]=7;
 const copy=duplicateProject(science,p.id,products,now);assert.deepEqual(copy.candidates,p.candidates);assert.deepEqual(copy.chosen,p.chosen);assert.notEqual(copy.id,p.id);
 const json=exportProject(p),payload=JSON.parse(json);assert.equal(payload.format,'perspektyva-project');assert.equal(payload.version,1);
 const state={science},h=helpers();handleScience('science-import',{text:json,size:new TextEncoder().encode(json).length},state,h);
 assert.equal(science.projects.length,3);assert.equal(science.projects[2].quantities[ids[2]],7);assert.deepEqual(normalizeScience(science),science);
 const before=snapshot(science);assert.throws(()=>create(science,65),/64/);assert.equal(snapshot(science),before);
 payload.project.candidates.push(ids[64]);payload.project.quantities[ids[64]]=1;const over=JSON.stringify(payload);
 assert.throws(()=>importProject(over,over.length),/64/);
 handleScience('science-import',{text:over,size:over.length},state,h);assert.equal(snapshot(science),before);assert.match(h.calls.messages.at(-1),/64/);
});

test('known inequality and incompleteness are independent; gaps stay visible in differences mode',()=>{
 const models=values=>values.map((value,i)=>({...byId('u02'),id:`test-${i}`,props:{...byId('u02').props,'Маса':value}}));
 for(const [values,expected] of [
  [[null,undefined],{different:false,incomplete:true}],
  [[null,'240 г'],{different:false,incomplete:true}],
  [['240 г','360 г',null],{different:true,incomplete:true}],
  [['240 г','360 г'],{different:true,incomplete:false}],
  [[0,null],{different:false,incomplete:true}],
  [[0,false],{different:true,incomplete:false}],
  [['не застосовується',null],{different:false,incomplete:true}],
  [['суперечливі дані','240 г',null],{different:true,incomplete:true}],
 ]){assert.deepEqual(comparisonStatus(models(values),'Маса'),expected);assert.ok(comparisonKeys(models(values),true).includes('Маса'));}
 assert.notEqual(semantic('не застосовується'),semantic(null));assert.notEqual(semantic('суперечливі дані'),semantic(null));
 assert.deepEqual(comparisonStatus(models(['240 г','240 Г']),'Маса'),{different:false,incomplete:false});
});

test('NG list and series omit commercial price/stock consistently with technical cards',()=>{
 const state=initialState();
 for(const view of ['list','series'])for(const brand of ['asp','ng']){
  const html=renderCatalog({route:{brand,params:new URLSearchParams({cat:'ups',view,q:'DEMO-U02'})},state,icon:()=>'',empty:()=>'',dock:()=>'',compareButton:()=>'',favoriteButton:()=>'',cartButton:()=>'',productCard:()=>''});
  assert.equal(html.replaceAll('\u00a0',' ').includes('<strong>2 190 грн</strong>'),brand==='asp');
  assert.equal(html.includes('Виконання D1 · технічний опис'),brand==='ng');
  if(brand==='ng')assert.ok(!html.includes('class="stock '));
 }
});

test('human TXT titles use current identity while the storage and project machine contracts stay stable',()=>{
 const state=initialState();state.cart={u02:3};
 assert.ok(listText(state).startsWith('ASP24 / NG Group —'));
 assert.ok(consultationText(byId('u02'),{purpose:'Тест',question:'Питання',quantity:''}).startsWith('ASP24 / NG Group —'));
 assert.equal(STATE_KEY,'perspective-demo-v1');assert.equal(state.version,4);
});

test('research resize restores replace scroll subscriptions and leaving the page cleans them up',()=>{
 const app=readFileSync(new URL('../app.js',import.meta.url),'utf8');
 const restore=app.slice(app.indexOf('function restoreResearch()'),app.indexOf('function updateContextSize()'));
 const scroll=new EventTarget(),header=new EventTarget();scroll.scrollLeft=0;header.scrollLeft=0;
 let saves=0,captures=0;
 const scope={AbortController,modern:false,modernComparisonActive(){return scope.modern;},route:{page:'compare'},state:{view:{group:'ups',research:{ups:{x:10,scroll:0}}}},researchScrollController:null,restoringResearch:false,
  $:selector=>selector==='.research-scroll'?scroll:header,researchRows:()=>[],scrollY:0,contextHeight:()=>0,
  window:{scrollTo(){}},document:{documentElement:{scrollHeight:1000}},innerHeight:900,
  captureResearch(){captures++;},save(){saves++;},updateContextSize(){}};
 runInNewContext(restore+';this.restore=restoreResearch;',scope);
 for(let i=0;i<5;i++)scope.restore();
 scroll.scrollLeft=100;scroll.dispatchEvent(new Event('scroll'));
 assert.equal(header.scrollLeft,100);assert.equal(captures,1);assert.equal(saves,1);
 header.scrollLeft=200;header.dispatchEvent(new Event('scroll'));assert.equal(scroll.scrollLeft,200);
 scope.route.page='catalog';scope.restore();scroll.dispatchEvent(new Event('scroll'));
 assert.equal(saves,1);
 scope.route.page='compare';scope.restore();scope.modern=true;scope.restore();
 scroll.dispatchEvent(new Event('scroll'));assert.equal(saves,1,'entering React pilot also aborts legacy subscriptions');
});
