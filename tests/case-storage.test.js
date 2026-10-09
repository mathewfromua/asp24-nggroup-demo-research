import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {isolatedStorage,seedCase,createCaseExport,validateCaseExport,caseStorageMessage,caseSaveLabel} from '../case-context.js';
import {readState,writeState,STATE_KEY} from '../logic.js';

const registry=JSON.parse(readFileSync(new URL('../publication.json',import.meta.url)));
const record=registry.cases.find(c=>c.caseId==='model-document');
const seed=()=>seedCase(record),key=`asp24-nggroup-case:${record.caseId}:v${record.caseVersion}`;
const draftId=Object.keys(seed().drafts)[0];
const typed='  Введений текст: XPON / 1 Гбіт/с\n«Не загубити» 👩‍🔧 — 0 ≠ невідомо.  ';
function fixture(initial){
  const entries=new Map([[STATE_KEY,'PERSONAL: cart + projects + drafts'],...(initial===undefined?[]:[[key,JSON.stringify(initial)]])]);
  const access=[],fault={};
  const backing={
    getItem(k){access.push(['get',k]);if(fault.read)throw new Error('read denied');return entries.get(k)??null;},
    setItem(k,v){access.push(['set',k]);if(fault.write)throw new Error('QuotaExceededError');entries.set(k,v);},
    removeItem(k){access.push(['remove',k]);if(fault.clear)throw new Error('clear denied');entries.delete(k);}
  };
  return {entries,access,fault,backing};
}
function edit(store,text=typed){const state=readState(store).state;state.drafts[draftId].question=text;return {state,ok:writeState(store,state)};}
function exported(store){const text=createCaseExport(record,readState(store).state),payload=JSON.parse(text);assert.equal(validateCaseExport(payload,record),null);return payload;}
function isolated(f){assert.equal(f.entries.get(STATE_KEY),'PERSONAL: cart + projects + drafts');assert.ok(f.access.every(([,name])=>name===key));}

test('successful writes persist exact draft, schema, case identity and quantities across reinitialization',()=>{
  const f=fixture(),store=isolatedStorage(f.backing,key,seed());
  assert.equal(store.status.kind,'persisted');assert.equal(edit(store).ok,true);
  const next=isolatedStorage(f.backing,key,seed());
  assert.equal(readState(next).state.drafts[draftId].question,typed);
  assert.equal(next.status.persisted,true);
  const payload=exported(next);assert.equal(payload.state.drafts[draftId].question,typed);
  assert.equal(payload.state.version,4);assert.equal(payload.stateSchemaVersion,4);assert.equal(payload.exportVersion,1);
  assert.equal(payload.caseId,record.caseId);assert.equal(payload.caseVersion,record.caseVersion);
  assert.deepEqual(payload.state.cart,seed().cart);isolated(f);
});

test('quota failure returns false, retains subsequent typed changes and exports the live draft',()=>{
  const f=fixture(),store=isolatedStorage(f.backing,key,seed());f.fault.write=true;
  assert.equal(edit(store,'first').ok,false);assert.equal(edit(store).ok,false);
  assert.deepEqual(store.status,{kind:'write-error',persisted:false});
  assert.equal(readState(store).state.drafts[draftId].question,typed);
  assert.equal(exported(store).state.drafts[draftId].question,typed);
  assert.notEqual(JSON.parse(f.entries.get(key)).drafts[draftId].question,typed);isolated(f);
});

test('unavailable sessionStorage is explicitly memory-only with a usable validated export',()=>{
  const store=isolatedStorage(undefined,key,seed());assert.equal(store.status.kind,'memory-only');
  assert.equal(edit(store).ok,false);assert.equal(store.status.persisted,false);
  assert.equal(exported(store).state.drafts[draftId].question,typed);
  assert.equal(store.reset().ok,false);assert.equal(store.status.kind,'clear-error');
  assert.equal(exported(store).state.drafts[draftId].question,typed);
});

test('read exception preserves unreadable previous state while new edits remain exportable',()=>{
  const old=seed();old.drafts[draftId].question='unreadable previous draft';
  const f=fixture(old);f.fault.read=true;const before=f.entries.get(key),store=isolatedStorage(f.backing,key,seed());
  assert.equal(store.status.kind,'read-error');assert.equal(edit(store).ok,false);
  assert.equal(store.status.kind,'read-error');assert.equal(f.entries.get(key),before);
  assert.equal(exported(store).state.drafts[draftId].question,typed);
  assert.equal(f.access.filter(([op])=>op==='set').length,0);isolated(f);
});

test('malformed and unsupported stored data are not silently overwritten',()=>{
  for(const raw of ['{broken',JSON.stringify({version:99,note:'keep me'})]){
    const f=fixture();f.entries.set(key,raw);const store=isolatedStorage(f.backing,key,seed());
    assert.equal(store.status.kind,'read-error');assert.equal(edit(store).ok,false);
    assert.equal(f.entries.get(key),raw);assert.equal(exported(store).state.drafts[draftId].question,typed);isolated(f);
  }
});

test('remove exception preserves working state and stale durable state, and reset can be retried',()=>{
  const f=fixture(),store=isolatedStorage(f.backing,key,seed());edit(store,'persisted');f.fault.write=true;
  edit(store);const before=f.entries.get(key);f.fault.clear=true;
  assert.equal(store.reset().ok,false);assert.equal(store.status.kind,'clear-error');
  assert.equal(f.entries.get(key),before);assert.equal(exported(store).state.drafts[draftId].question,typed);
  assert.equal(edit(store,typed+' edited after failed reset').ok,false);
  assert.equal(exported(store).state.drafts[draftId].question,typed+' edited after failed reset');
  f.fault.clear=false;assert.equal(store.reset().ok,true);assert.equal(f.entries.has(key),false);
  assert.equal(readState(store).state.drafts[draftId].question,seed().drafts[draftId].question);isolated(f);
});

test('successful reset rejects stale pagehide writes from the outgoing application instance',()=>{
  const f=fixture(),store=isolatedStorage(f.backing,key,seed());const {state}=edit(store);
  assert.equal(store.reset().ok,true);assert.equal(writeState(store,state),false);
  const next=isolatedStorage(f.backing,key,seed());
  assert.equal(readState(next).state.drafts[draftId].question,seed().drafts[draftId].question);isolated(f);
});

test('reload after memory-only cannot claim lost live edits survived, while exported copy retains them',()=>{
  const f=fixture(),store=isolatedStorage(f.backing,key,seed());f.fault.write=true;edit(store);
  const downloaded=exported(store),next=isolatedStorage(f.backing,key,seed());
  assert.equal(readState(next).state.drafts[draftId].question,seed().drafts[draftId].question);
  assert.equal(downloaded.state.drafts[draftId].question,typed);
  assert.match(caseStorageMessage(store.status),/перезавантаження.*втратити/);
  assert.match(caseSaveLabel(store.status),/Лише в пам’яті/);isolated(f);
});

test('reinitialization with no backing starts a fixture and never silently claims durable success',()=>{
  const store=isolatedStorage(null,key,seed());edit(store);
  const next=isolatedStorage(null,key,seed());
  assert.equal(next.status.kind,'memory-only');assert.equal(next.status.persisted,false);
  assert.equal(readState(next).state.drafts[draftId].question,seed().drafts[draftId].question);
});

test('persistence recovers only after an actual successful write',()=>{
  const f=fixture(),store=isolatedStorage(f.backing,key,seed());f.fault.write=true;edit(store);
  assert.equal(store.status.persisted,false);f.fault.write=false;assert.equal(edit(store).ok,true);
  assert.deepEqual(store.status,{kind:'persisted',persisted:true});
  assert.equal(readState(isolatedStorage(f.backing,key,seed())).state.drafts[draftId].question,typed);isolated(f);
});

test('successful explicit reset releases read-error protection without reading personal state',()=>{
  const f=fixture(seed());f.fault.read=true;const store=isolatedStorage(f.backing,key,seed());edit(store);
  assert.equal(store.reset().ok,true);f.fault.read=false;
  const next=isolatedStorage(f.backing,key,seed());assert.equal(edit(next).ok,true);isolated(f);
});

test('failed transaction restores live memory without retrying storage',()=>{
  const f=fixture(),store=isolatedStorage(f.backing,key,seed()),current=readState(store).state;
  f.fault.write=true;edit(store,'uncommitted next state');const count=f.access.length;
  store.retainState(current);assert.equal(f.access.length,count);
  assert.equal(exported(store).state.drafts[draftId].question,current.drafts[draftId].question);isolated(f);
});

test('every failure has distinct explicit accessible text and no successful-save wording',()=>{
  const messages=new Set();
  for(const kind of ['memory-only','read-error','write-error','clear-error']){
    const status={kind,persisted:false},message=caseStorageMessage(status),label=caseSaveLabel(status);messages.add(message);
    assert.match(message,/пам’яті цієї вкладки/);assert.match(message,/JSON/);assert.match(message,/перезавантаження.*втратити/);
    assert.doesNotMatch(label,/Збережено|зберігається|збережено в/);
  }
  assert.equal(messages.size,4);
});

test('status observers report actual failure and recovery and can unsubscribe',()=>{
  const f=fixture(),store=isolatedStorage(f.backing,key,seed()),seen=[],off=store.subscribe(s=>seen.push(s.kind));
  f.fault.write=true;edit(store);f.fault.write=false;edit(store);off();edit(store,'next');
  assert.deepEqual(seen,['persisted','write-error','persisted']);
});

test('export validation rejects unknown schemas, wrong case, broken draft and invalid candidate identity',()=>{
  const state=seed(),good=JSON.parse(createCaseExport(record,state));
  for(const mutate of [p=>p.state.version=3,p=>p.exportVersion=2,p=>p.stateSchemaVersion=5,p=>p.caseId='another-case',p=>p.state.drafts[draftId].question=42,p=>p.state.cart.unknown=1,p=>p.state.compareByGroup.ups=['unknown'],p=>p.state.view.pairs.ups=['unknown'],p=>p.state.orders=[{}],p=>p.state.science={version:1,projects:[{}]}]){
    const invalid=structuredClone(good);mutate(invalid);assert.notEqual(validateCaseExport(invalid,record),null);
  }
  state.drafts[draftId].question=42;assert.throws(()=>createCaseExport(record,state),/чернетка/);
});

test('all four cases keep private keys isolated through success, failed writes, reset and exports',()=>{
  for(const c of registry.cases){
    const f=fixture(),caseKey=`asp24-nggroup-case:${c.caseId}:v${c.caseVersion}`,store=isolatedStorage(f.backing,caseKey,seedCase(c));
    const s=readState(store).state;s.note=typed;assert.equal(writeState(store,s),true);f.fault.write=true;s.note+='+';assert.equal(writeState(store,s),false);
    const payload=JSON.parse(createCaseExport(c,s));assert.equal(validateCaseExport(payload,c),null);assert.equal(payload.state.note,typed+'+');
    store.reset();assert.equal(f.entries.get(STATE_KEY),'PERSONAL: cart + projects + drafts');assert.ok(f.access.every(([,name])=>name===caseKey));
  }
  assert.throws(()=>isolatedStorage(fixture().backing,STATE_KEY,seed()),/Unexpected case storage key/);
});
