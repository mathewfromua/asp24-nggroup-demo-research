import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {products,groups,byId,numericValue,reelLength} from '../data.js';
import {initialState,migrateState,readState,writeState,filterProducts,quantityLabel,cartTotal,listText,addComparison,removeComparison,undoComparison,validRoute,STATE_KEY} from '../logic.js';
import {createDemoOrder,restoreOrders,inspectOrders,repeatOrder,orderText} from '../orders.js';

const legacy=JSON.parse(readFileSync(new URL('./legacy-catalog.json',import.meta.url)));
const now='2026-10-07T19:00:00.000Z';
const makeOrder=(cart,catalog=products)=>createDemoOrder({...initialState(),cart},{alias:'Демо'},{now,id:'demo-20261007-012345abcdef',catalog});

test('Catalogue: 384 unique models; eight varied groups; old 15 technical and commercial records exact',()=>{
 assert.equal(products.length,384);assert.equal(Object.keys(groups).length,8);
 for(const group of Object.keys(groups))assert.equal(products.filter(p=>p.group===group).length,({ups:48,optics:64,switches:64,cable:56,wifi:48,splitters:40,meters:32,injectors:32})[group]);
 for(const key of ['id','sku','name'])assert.equal(new Set(products.map(p=>p[key])).size,384,key);
 for(const p of products){assert.equal(p.isDemo,true);assert.equal(p.sourceKind,'synthetic-ui-fixture');assert.equal(p.typeLabel,groups[p.group].typeLabel);assert.ok(p.family);}
 for(const old of legacy){const current=byId(old.id);for(const key of ['id','sku','code','group','price','available','props','ng','unit','revision'])assert.deepEqual(current[key],old[key],old.id+' '+key);}
});

test('Every old name, exact SKU and new name resolves the same stable ID',()=>{
 for(const old of legacy)for(const query of [old.name,old.sku,...old.aliases,byId(old.id).name])assert.equal(filterProducts('asp',new URLSearchParams({q:query}))[0].id,old.id,query);
 for(const p of products)assert.equal(filterProducts('asp',new URLSearchParams({q:p.sku}))[0].id,p.id);
});

test('Numeric ordering preserves decimal speeds, null last, both directions',()=>{
 for(const [group,g]of Object.entries(groups))for(const [key]of g.numericFacetDefinitions)for(const direction of ['up','down']){
  const result=filterProducts('asp',new URLSearchParams({cat:group,sort:key+'-'+direction}));
  const known=result.map(p=>numericValue(p,key)).filter(v=>v!==null);
  assert.deepEqual(known,[...known].sort((a,b)=>(a-b)*(direction==='down'?-1:1)));
  const firstNull=result.findIndex(p=>numericValue(p,key)===null);if(firstNull>=0)assert.ok(result.slice(firstNull).every(p=>numericValue(p,key)===null));
 }
 const fixture=[10,2.5,25,1].map((value,index)=>({...byId('o01'),id:'speed-test-'+index,numericFacets:{speedGbps:{value}}}));
 const speeds=filterProducts('asp',new URLSearchParams({cat:'optics',sort:'speedGbps-up'}),fixture).map(p=>numericValue(p,'speedGbps'));
 assert.deepEqual([...new Set(speeds)],[1,2.5,10,25]);
 assert.equal(numericValue(byId('u01'),'massG'),null);assert.equal(numericValue(byId('s01'),'sfpPorts'),0);
});

test('Repeated categorical values are OR within one facet; distinct facets and numeric boundaries are AND',()=>{
 const params=new URLSearchParams('cat=ups');params.append('f0','18 Вт');params.append('f0','36 Вт');params.set('f1','9 / 12 В');params.set('n_energyWh_min','60');
 assert.deepEqual(filterProducts('asp',params).map(p=>p.id),['u02','u04','u10','u34']);
 const speed=new URLSearchParams({cat:'optics',n_speedGbps_min:'2,5',n_speedGbps_max:'10'});
 assert.ok(filterProducts('asp',speed).every(p=>numericValue(p,'speedGbps')>=2.5&&numericValue(p,'speedGbps')<=10));
 speed.set('n_speedGbps_min','not-number');assert.deepEqual(filterProducts('asp',speed),[]);
});

test('Cable physical lengths and totals follow each actual unit across cart, TXT and frozen orders',()=>{
 for(const [id,total,length]of [['c02',518000,200],['c04',1038000,610]]){
  const state={...initialState(),cart:{[id]:2}},order=makeOrder(state.cart);
  assert.equal(cartTotal(state.cart),total);assert.equal(order.total,total);assert.equal(reelLength(byId(id))*2,length);
  assert.ok(quantityLabel(byId(id),2).includes(length+' м'));assert.ok(listText(state).includes(length+' м'));assert.ok(orderText(order).includes(length+' м'));
  assert.deepEqual(restoreOrders(JSON.parse(JSON.stringify([order]))),[order]);
 }
 assert.equal(makeOrder({u02:3}).total,657000);
});

test('Historical order names/units/prices stay frozen; repeat uses ID and describes renamed/unavailable models',()=>{
 const oldOrder=makeOrder({u02:3,c02:2},legacy);const frozen=JSON.stringify(oldOrder);
 assert.equal(oldOrder.items[0].name,'Резерв 36');assert.equal(restoreOrders([oldOrder])[0].items[0].name,'Резерв 36');
 const result=repeatOrder({},oldOrder);assert.deepEqual(result.cart,{u02:3,c02:2});assert.deepEqual(result.renamed[0],{id:'u02',from:'Резерв 36',to:'VOLTYN N36'});assert.equal(JSON.stringify(oldOrder),frozen);
 const changed=products.map(p=>p.id==='u02'?{...p,available:false,availabilityState:'unavailable'}:p);
 const unavailable=repeatOrder({},oldOrder,changed);assert.deepEqual(unavailable.skipped,['DEMO-U02']);assert.equal(unavailable.changedStatus[0].to,'unavailable');
 const historic305={...makeOrder({c04:2})};delete historic305.items[0].unitDefinition;
 assert.equal(restoreOrders([historic305])[0].items[0].unit,'бухта 305 м');assert.ok(orderText(restoreOrders([historic305])[0]).includes('610 м'));
});

test('Invalid, duplicate and excess order records are quarantined; original formatted raw survives writes',()=>{
 const order=makeOrder({u02:3}),invalid={id:'broken',items:[{name:'<img onerror=alert(1)>'}]};
 const raw=JSON.stringify({cart:{u02:3},orders:[order,invalid,order],science:{projects:[{id:'untouched'}]}},null,2);
 let stored=raw;const mem={getItem:()=>stored,setItem:(key,value)=>{assert.equal(key,STATE_KEY);stored=value;}};
 const read=readState(mem);assert.equal(read.status,'recovery');assert.equal(read.state.orders.length,1);assert.equal(read.state.recovery.rawState,raw);assert.equal(read.state.recovery.quarantinedOrders.length,2);
 read.state.note='Нова примітка';assert.equal(writeState(mem,read.state),true);
 const again=readState(mem);assert.equal(again.status,'recovery');assert.equal(again.state.recovery.rawState,raw);assert.equal(again.state.recovery.quarantinedOrders.length,2);assert.deepEqual(again.state.cart,{u02:3});
 assert.equal(inspectOrders('not an array').quarantined.length,1);
 const excess=Array.from({length:101},(_,i)=>({...order,id:'demo-20261007-'+String(i).padStart(12,'0')}));assert.equal(inspectOrders(excess).orders.length,100);assert.equal(inspectOrders(excess).quarantined.length,1);
});

test('Corrupt storage raw remains recoverable; failed writes leave source state and storage unchanged',()=>{
 let raw='{bad json';const mem={getItem:()=>raw,setItem:(k,v)=>{raw=v;}};
 const read=readState(mem);assert.equal(read.status,'corrupt');assert.equal(read.state.recovery.rawState,'{bad json');
 assert.equal(writeState(mem,initialState()),true);assert.equal(JSON.parse(raw).recovery.rawState,'{bad json');
 const state=initialState();state.cart={u02:3};const frozen=JSON.stringify(state),before=raw;
 assert.equal(writeState({getItem:()=>raw,setItem:()=>{throw new Error('quota');}},state),false);assert.equal(raw,before);assert.equal(JSON.stringify(state),frozen);
});

test('All eight real groups support six candidates, seventh explicit replacement and undo without cross-group loss',()=>{
 for(const group of Object.keys(groups)){
  const state=initialState(),ids=products.filter(p=>p.group===group).map(p=>p.id);
  ids.slice(0,6).forEach(id=>assert.equal(addComparison(state,id),'ok'));
  state.view.pairs[group]=[ids[1],ids[3]];const before=JSON.stringify(state);assert.equal(addComparison(state,ids[6]),'limit');assert.equal(JSON.stringify(state),before);
  assert.equal(addComparison(state,ids[6],ids[1]),'ok');assert.deepEqual(state.view.pairs[group],[ids[6],ids[3]]);
  const token=removeComparison(state,ids[6]);assert.equal(undoComparison(state,token),true);assert.equal(state.compareByGroup[group][1],ids[6]);
 }
});

test('Science state, catalog view and comparison detail context survive migration; routes reject executable values',()=>{
 const state=initialState();state.science={version:1,projects:[{id:'example',name:'<script>not executed</script>'}]};state.view.catalogViews={asp:'series',ng:'list'};state.view.comparisonDialog={type:'details',id:'u02'};
 assert.deepEqual(migrateState(state),state);
 assert.equal(migrateState({...state,view:{...state.view,catalogViews:{asp:'family'}}}).view.catalogViews.asp,'series');
 for(const route of ['#/asp/projects','#/ng/project/example','#/asp/templates','#/ng/lab','#/asp/lab/null-zero','#/asp/model-map'])assert.equal(validRoute(route),true);
 for(const route of ['#/asp/project/<script>','javascript:alert(1)','#/ng/lab/../../'])assert.equal(validRoute(route),false);
});
