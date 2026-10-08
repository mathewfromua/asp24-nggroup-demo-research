import test from 'node:test';
import assert from 'node:assert/strict';
import { products, byId } from '../data.js';
import { initialState, migrateState, readState, writeState, filterProducts, validRoute } from '../logic.js';
import { createDemoOrder, createOrderId, transitionOrder, restoreOrders, repeatOrder, sanitizeCheckout, orderText, MAX_ORDERS } from '../orders.js';
import { readable } from '../presentation.js';
const now='2026-09-29T08:00:00.000Z', id='demo-20260929-aabbccddeeff';
function make(cart={u02:3,c02:2}) {const s=initialState();s.cart=cart;return createDemoOrder(s,{alias:'Демо-покупець',delivery:'pickup',payment:'invoice'}, {now,id});}

test('Order snapshot has exact IDs, integer money and cable units',()=>{
 const o=make();assert.equal(o.total,1175000);assert.equal(o.items[0].sku,'DEMO-U02');assert.equal(o.items[0].quantity,3);assert.equal(o.items[1].unit,'бухта 100 м');assert.equal(o.localOnly,true);assert.equal(o.currency,'UAH');assert.deepEqual(o.history,[{status:'created',at:now}]);
});
test('Creation is pure and does not change the cart, catalogue or existing orders',()=>{
 const s=initialState();s.cart={u02:3};const saved=structuredClone(s);const cat=structuredClone(products);const o=createDemoOrder(s,{alias:'A'},{now,id,catalog:cat});assert.deepEqual(s,saved);cat.find(p=>p.id==='u02').price=1;assert.equal(o.items[0].unitPrice,219000);assert.equal(o.total,657000);
});
test('Reject empty/unavailable/invalid-quantity orders, including exponent and overflow',()=>{
 for(const cart of [{},{u03:1},{bad:1},{u02:0},{u02:-1},{u02:1000},{u02:1.1},{u02:'3'},{u02:NaN}])assert.throws(()=>make(cart));
});
test('Alias is required; checkout keeps no unknown contact or payment fields',()=>{
 const c=sanitizeCheckout({alias:'  Демо  ',delivery:'fake',payment:'visa',email:'private',card:'secret',note:'x'.repeat(1000)});assert.deepEqual(Object.keys(c),['alias','delivery','payment','note']);assert.equal(c.alias,'Демо');assert.equal(c.delivery,'pickup');assert.equal(c.payment,'invoice');assert.equal(c.note.length,600);
 const s=initialState();s.cart={u02:1};assert.throws(()=>createDemoOrder(s,{alias:'   '},{now,id}),/ALIAS_REQUIRED/);
});
test('Order IDs and limits are validated; duplicate IDs are rejected',()=>{
 const s=initialState();s.cart={u02:1};s.orders=[make()];assert.throws(()=>createDemoOrder(s,{alias:'A'},{now,id}),/DUPLICATE_ID/);
 s.orders=Array.from({length:MAX_ORDERS},(_,i)=>({...make(),id:'demo-20260929-'+i}));assert.throws(()=>createDemoOrder(s,{alias:'A'},{now,id:'demo-something-else'}),/ORDER_LIMIT/);
 assert.equal(createOrderId(new Date(now),'aabbccdd-1122-3344-5566-778899001122'),'demo-20260929-aabbccdd1122');
});
test('All five stages are sequential, final stage and cancellation cannot advance',()=>{
 let o=make();const before=structuredClone(o);
 for(const [i,s] of ['confirmed','packed','shipped','completed'].entries()){o=transitionOrder(o,'next',`2026-09-29T08:0${i+1}:00.000Z`);assert.equal(o.status,s);}
 assert.deepEqual(before,make());assert.equal(o.history.length,5);assert.equal(transitionOrder(o,'next'),null);assert.equal(transitionOrder(o,'cancel'),null);
});
test('Cancellation allowed only before shipment; history cannot move back in time',()=>{
 let o=make();assert.equal(transitionOrder(o,'next','2020-01-01T00:00:00.000Z'),null);
 const c=transitionOrder(o,'cancel',now);assert.equal(c.status,'cancelled');assert.equal(transitionOrder(c,'next'),null);
 for(let i=0;i<3;i++)o=transitionOrder(o,'next',now);assert.equal(o.status,'shipped');assert.equal(transitionOrder(o,'cancel',now),null);
});
test('Stored snapshot round-trips; tampered total is recomputed',()=>{
 const o=make();assert.deepEqual(restoreOrders([o]),[o]);assert.equal(restoreOrders([{...o,total:1}])[0].total,1175000);assert.deepEqual(restoreOrders([o,o]),[o]);
});
test('Malformed records and impossible histories are not restored as valid orders',()=>{
 const o=make();for(const wrong of [{},{...o,id:'__proto__'},{...o,items:[]},{...o,items:[{...o.items[0],quantity:-1}]},{...o,status:'completed'}, {...o,history:[{status:'created',at:now},{status:'completed',at:now}],status:'completed'},{...o,items:[...o.items,o.items[0]]}])assert.deepEqual(restoreOrders([wrong]),[]);
 for(const raw of [null,4,'x',{},[{a:2}]])assert.deepEqual(restoreOrders(raw),[]);
});
test('Schema 4 migrates old selection without dropping it; adds empty order history',()=>{
 const old={version:3,cart:{u02:3},favorites:['u04'],compareByGroup:{ups:['u02','u04']},view:{group:'ups',pairs:{ups:['u04','u02']},differences:true}};
 const s=migrateState(old);assert.equal(s.version,4);assert.deepEqual(s.cart,{u02:3});assert.deepEqual(s.view.pairs.ups,['u04','u02']);assert.deepEqual(s.orders,[]);
 s.orders=[make()];s.checkout={alias:'A',delivery:'demo-delivery',payment:'demo-card',note:'N'};assert.deepEqual(migrateState(JSON.parse(JSON.stringify(s))),s);
});
test('Persistence failure cannot mutate source snapshots; valid storage round-trips orders',()=>{
 const s=initialState();s.orders=[make()];let text='';const mem={getItem(){return text},setItem(k,v){text=v}};assert.equal(writeState(mem,s),true);assert.deepEqual(readState(mem).state.orders,s.orders);
 const saved=structuredClone(s);assert.equal(writeState({setItem(){throw new Error('quota')}},s),false);assert.deepEqual(s,saved);
});
test('Repeat adds to existing cart without overwriting; skips unavailable and caps at 999',()=>{
 const o=make();const r=repeatOrder({u02:2,s01:1},o);assert.deepEqual(r.cart,{u02:5,s01:1,c02:2});assert.equal(o.items[0].quantity,3);
 const cat=products.map(p=>p.id==='c02'?{...p,available:false}:p);const b=repeatOrder({u02:998},o,cat);assert.equal(b.cart.u02,999);assert.deepEqual(b.skipped,['DEMO-C02']);assert.deepEqual(b.clamped,['DEMO-U02']);
});
test('TXT states local-only status and carries exact items, total and transitions',()=>{
 const o=transitionOrder(make(),'next',now),t=orderText(o);assert.ok(t.includes('DEMO-U02'));assert.ok(t.includes('11\u00a0750 грн'));assert.ok(t.includes('нічого')||t.includes('Нічого'));assert.ok(t.includes('Підтверджено'));assert.ok(t.includes('бухта 100 м'));
});
test('Names are short and consistent; all previous release names remain searchable',()=>{
 assert.equal(byId('u04').name,'VOLTYN N36 Arc');assert.equal(byId('c02').family,'STRUNEX');
 for(const p of products)for(const alias of p.aliases)assert.ok(filterProducts('asp',new URLSearchParams({q:alias})).some(x=>x.id===p.id));
});
test('Numeric rendering protects whole integers and escapes text without corrupting entities',()=>{
 assert.equal(readable('36'),'<span class="numeric-token">36</span>');assert.ok(readable('1\u00a0290 грн').includes('>1\u00a0290</span>'));
 assert.ok(readable('Резерв 36+').includes('>36+</span>'));assert.equal(readable("x' <img>"),'x&#39; &lt;img&gt;');assert.ok(!readable('<script>12</script>').includes('<script>'));
});
test('New order routes are accepted; malformed routes and unsupported actions are rejected',()=>{
 for(const path of ['#/asp/checkout','#/asp/orders','#/asp/order/'+id])assert.equal(validRoute(path),true);
 for(const path of ['#/asp/order/<script>','javascript:alert(1)','#/asp/orders/../../'])assert.equal(validRoute(path),false);
});
