import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {seedCase,isolatedStorage} from '../case-context.js';
import {STATE_KEY,readState,writeState,cartTotal} from '../logic.js';
import {byId,reelLength} from '../data.js';
const registry=JSON.parse(readFileSync(new URL('../publication.json',import.meta.url)));
const manuscript=JSON.parse(readFileSync(new URL('../reports/content.json',import.meta.url)));
test('each immutable case binds an existing section and deterministic current fixtures',()=>{
 assert.equal(registry.cases.length,4);
 for(const c of registry.cases){
  assert.ok(manuscript[c.reportId].some(p=>p.id===c.sectionId));
  const s=seedCase(c);
  for(const id of [...(c.seed.candidates||[]),...Object.keys(c.seed.cart||{}),...Object.keys(c.seed.drafts||{})])assert.ok(byId(id));
  assert.equal(s.version,4);
 }
 const s=seedCase(registry.cases.find(c=>c.caseId==='two-reels'));
 assert.equal(cartTotal(s.cart),1695000);assert.equal(reelLength(byId('c04'))*2,610);
 const c=registry.cases.find(c=>c.caseId==='unknown-and-difference');
 assert.deepEqual(c.seed.candidates.map(id=>byId(id).props['Маса']),[null,'520 г','860 г']);
});
test('case state survives reload separately; reset and write failure never read or alter personal state',()=>{
 const entries=new Map([[STATE_KEY,'personal cart, drafts, projects']]),access=[];
 const backing={getItem(k){access.push(['get',k]);return entries.get(k)||null;},setItem(k,v){access.push(['set',k]);entries.set(k,v);},removeItem(k){access.push(['remove',k]);entries.delete(k);}};
 const c=registry.cases[0],key='asp24-nggroup-case:six-candidates:v1',seed=seedCase(c);
 const store=isolatedStorage(backing,key,seed),s=readState(store).state;s.note='case only';assert.ok(writeState(store,s));
 assert.equal(readState(isolatedStorage(backing,key,seed)).state.note,'case only');
 store.reset();assert.equal(readState(store).state.note,'');
 assert.equal(entries.get(STATE_KEY),'personal cart, drafts, projects');assert.ok(access.every(([,k])=>k===key));
 assert.throws(()=>store.setItem('other','x'));
 const denied=isolatedStorage({getItem(){throw Error('denied')},setItem(){throw Error('denied')}},key,seed);
 assert.ok(writeState(denied,s));assert.equal(readState(denied).state.note,'case only');
});
