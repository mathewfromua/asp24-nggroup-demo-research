import test from 'node:test';
import assert from 'node:assert/strict';
import {products,groups,byId,display} from '../data.js';
import * as L from '../logic.js';
const ups=products.filter(p=>p.group==='ups').slice(0,6).map(p=>p.id);
const ids=result=>result.map(p=>p.id);
function six(){const s=L.initialState();ups.forEach(id=>L.toggleComparison(s,id));return s;}

test('Catalog inventory, stable price and exact document mapping',()=>{
 assert.equal(products.length,384);assert.equal(new Set(ids(products)).size,384);assert.equal(new Set(products.map(p=>p.sku)).size,384);assert.equal(byId('u02').price,219000);
 for(const p of products){assert.ok(groups[p.group]);assert.ok(p.unit);assert.equal(Number.isInteger(p.price),true);assert.ok(p.price>0);assert.equal(typeof p.available,'boolean');assert.equal(p.revision,'D1');for(const key of groups[p.group].keys)assert.equal(typeof display(p.props[key]),'string');assert.equal(byId(p.id),p);}
});
test('Filter returns every expected ID and excludes others, every category/brand/facet',()=>{
 for(const brand of ['asp','ng'])for(const cat of ['all',...Object.keys(groups)]){
  const base=products.filter(p=>(brand==='asp'||p.ng)&&(cat==='all'||p.group===cat));
  assert.deepEqual(ids(L.filterProducts(brand,new URLSearchParams({cat}))),ids(base));
  if(cat!=='all')for(const [i,key] of groups[cat].filters.entries())for(const v of new Set(base.map(p=>display(p.props[key]))))assert.deepEqual(ids(L.filterProducts(brand,new URLSearchParams({cat,['f'+i]:v}))),ids(base.filter(p=>display(p.props[key])===v)));
 }
 assert.deepEqual(ids(L.filterProducts('asp',new URLSearchParams({cat:'cable',f0:'Cu',f1:'Надворі'}))),ids(products.filter(p=>p.group==='cable'&&p.props['Матеріал']==='Cu'&&p.props['Застосування']==='Надворі')));
 for(const p of products)assert.deepEqual(ids(L.filterProducts('asp',new URLSearchParams({q:p.sku.toLowerCase()}))),[p.id]);
 assert.deepEqual(ids(L.filterProducts('asp',new URLSearchParams({q:'demou02'}))),['u02']);
 assert.deepEqual(L.filterProducts('asp',new URLSearchParams({q:'неіснуюча модель'})),[]);
 assert.deepEqual(ids(L.filterProducts('asp',new URLSearchParams({available:'1'}))),ids(products.filter(p=>p.available)));
 for(const sort of ['price-up','price-down']){const values=L.filterProducts('asp',new URLSearchParams({sort})).map(p=>p.price);assert.deepEqual(values,[...values].sort((a,b)=>sort==='price-up'?a-b:b-a));}
});
test('C01/C02 0→1→2→3→4→6, seventh fixture rejected with original six intact',()=>{
 const s=L.initialState();assert.deepEqual(s.compareByGroup.ups,[]);for(const [i,id]of ups.entries()){assert.equal(L.toggleComparison(s,id),'ok');assert.deepEqual(s.compareByGroup.ups,ups.slice(0,i+1));}
 const fixture={...byId('u01'),id:'test-only-seventh',sku:'TEST-7'};
 assert.equal(L.toggleComparison(s,fixture.id,[...products,fixture]),'limit');assert.deepEqual(s.compareByGroup.ups,ups);assert.equal(products.some(p=>p.id===fixture.id),false);
});
test('C03/C04 all first/middle/last removals, re-adds and orders preserve stable IDs and groups',()=>{
 for(const removed of ups){const s=six();L.toggleComparison(s,'o01');L.toggleComparison(s,removed);assert.deepEqual(s.compareByGroup.ups,ups.filter(id=>id!==removed));assert.deepEqual(s.compareByGroup.optics,['o01']);L.toggleComparison(s,removed);assert.equal(s.compareByGroup.ups.at(-1),removed);assert.equal(new Set(s.compareByGroup.ups).size,6);
 for(const id of ups){L.moveComparison(s,'ups',id,-1);L.moveComparison(s,'ups',id,1);assert.deepEqual([...s.compareByGroup.ups].sort(),[...ups].sort());}
 for(const id of s.compareByGroup.ups){const before={...s.cart};const result=L.addCartItem(s,id);if(byId(id).available){assert.equal(result,'ok');assert.equal(s.cart[id],(before[id]||0)+1);}else{assert.equal(result,'unavailable');assert.deepEqual(s.cart,before);}}
 }
});
test('C05 semantic differences: whitespace, case, numeric formatting, units, null/zero/false',()=>{
 for(const [a,b]of [['36 ВТ','36 вт'],['1 000,00 Вт','1000.0 вт'],['5,5 × 2,1 мм','5.50×2.10 ММ'],['  LC   duplex  ','lc duplex'],[0,'0']])assert.equal(L.semantic(a),L.semantic(b),`${a} and ${b}`);
 for(const [a,b]of [[null,0],[null,false],[0,false],['1 Вт','1 кВт'],['1 м','1 км']])assert.notEqual(L.semantic(a),L.semantic(b));
 assert.equal(L.semantic(null),L.semantic(undefined));assert.deepEqual(L.comparisonKeys([],true),[]);assert.deepEqual(L.comparisonKeys([byId('u02')],true),[]);
 assert.deepEqual(L.comparisonKeys([byId('u02'),{...byId('u02'),id:'same'}],true),[]);
 assert.ok(L.comparisonKeys(ups.map(byId),true).includes('Маса'));assert.ok(!L.comparisonKeys(ups.map(byId),true).includes('Полярність'));
});
test('C06 mobile pair replacement/swap retains full group; diff uses selected pair',()=>{
 const s=six();let pair=L.visiblePair(ups);assert.deepEqual(pair,['u01','u02']);pair=L.selectPair(ups,pair,0,'u04');pair=L.selectPair(ups,pair,1,'u06');assert.deepEqual(pair,['u04','u06']);assert.deepEqual(s.compareByGroup.ups,ups);
 assert.deepEqual(L.selectPair(ups,pair,0,'u06'),['u06','u04']);assert.deepEqual(L.visiblePair(['u06'],pair),['u06']);
 assert.deepEqual(L.comparisonKeys(['u02','u04'].map(byId),true),['Запас енергії','Маса']);
});
test('C08/N02 state migration preserves legacy data, six IDs, groups, context/drafts',()=>{
 const legacy={cart:{u02:3,ghost:9,u03:1},favorites:['u02','bad','u02'],compare:[...ups,'o01','ghost'],listName:'Об’єкт <b>',note:'Примітка'};
 const s=L.migrateState(legacy);assert.deepEqual(s.cart,{u02:3});assert.deepEqual(s.favorites,['u02']);assert.deepEqual(s.compareByGroup.ups,ups);assert.deepEqual(s.compareByGroup.optics,['o01']);assert.equal(s.note,legacy.note);assert.equal(s.listName,legacy.listName);
 s.catalogs.asp='#/asp/catalog?cat=cable&f0=Cu&f1=Надворі&sort=price-up';s.view.differences=true;s.view.group='optics';s.drafts.u02={purpose:'Тест',quantity:'',question:'Яке підключення?'};assert.deepEqual(L.migrateState(JSON.parse(JSON.stringify(s))),s);
 for(const raw of [null,4,'text',[],{cart:[],favorites:'bad',compareByGroup:4,view:'x',drafts:8}])assert.doesNotThrow(()=>L.migrateState(raw));
 assert.equal(L.migrateState({catalogs:{asp:'https://evil.example',ng:'#/asp/catalog'}}).catalogs.asp,'');assert.equal(L.validRoute('javascript:alert(1)'),false);assert.equal(L.validRoute('#/asp/not-real'),false);
});
test('Storage normal, malformed JSON, denied read/write have accurate statuses',()=>{
 let raw=null;const mem={getItem(){return raw;},setItem(k,v){raw=v;}};const s=six();assert.equal(L.writeState(mem,s),true);assert.deepEqual(L.readState(mem).state,s);raw='{bad';assert.equal(L.readState(mem).status,'corrupt');
 const denied={getItem(){throw new Error('denied');},setItem(){throw new Error('denied');}};assert.equal(L.readState(denied).status,'denied');assert.equal(L.writeState(denied,s),false);assert.equal(L.readState(undefined).status,'denied');
});
test('B01/B02 stable u02 ×3 =657000 cents, unavailable and boundaries; repeated additions',()=>{
 const s=L.initialState();L.toggleComparison(s,'u01');L.toggleComparison(s,'u02');L.toggleComparison(s,'u01');for(let i=0;i<3;i++)L.addCartItem(s,'u02');assert.deepEqual(s.cart,{u02:3});assert.equal(L.cartTotal(s.cart),657000);assert.equal(L.cartTotal(L.migrateState(s).cart),657000);
 for(const q of [1,2,999,'1','2','999'])assert.equal(L.quantity(q),Number(q));for(const q of [0,-1,1.5,1000,'',' ','text','1e2','1.5'])assert.equal(L.quantity(q),null);
 for(let i=3;i<999;i++)assert.equal(L.addCartItem(s,'u02'),'ok');assert.equal(L.addCartItem(s,'u02'),'limit');assert.equal(s.cart.u02,999);assert.equal(L.cartTotal(s.cart),999*219000);assert.equal(L.addCartItem(s,'u03'),'unavailable');
 for(const p of products.filter(p=>p.available))for(const q of [1,2,999])assert.equal(L.cartTotal({[p.id]:q}),p.price*q);
});
test('B03/B04 same source for totals, labels and TXT, cable units and user text unchanged',()=>{
 const s=L.initialState();s.cart={c02:2,u02:3};s.listName='<img src=x onerror=alert(1)>';s.note='Примітка & <b>текст</b>';const txt=L.listText(s);assert.equal(L.cartTotal(s.cart),1175000);assert.ok(txt.includes('2 бухти · 200 м'));assert.ok(txt.includes('DEMO-C02'));assert.ok(txt.includes('11 750 грн'));assert.ok(txt.includes(s.note));assert.ok(txt.includes(s.listName));
});
test('G02 optional quantity and consultation text retains exact model/question',()=>{
 const d={purpose:'Сумісність',quantity:'',question:'  Чи можна так підключити?  '};const text=L.consultationText(byId('u02'),d);assert.ok(text.includes('DEMO-U02 | виконання D1'));assert.ok(text.includes('Кількість: Не визначена'));assert.ok(text.includes('Чи можна так підключити?'));assert.ok(text.includes('Нічого не надіслано'));
});
test('Ukrainian 1/2/5/11/21/22/25 plural forms',()=>{
 const expected=['1 модель','2 моделі','5 моделей','11 моделей','21 модель','22 моделі','25 моделей'];assert.deepEqual([1,2,5,11,21,22,25].map(L.modelCount),expected);
});

test('Legacy display names remain search aliases after editorial renaming',()=>{
 for(const p of products.filter(p=>p.legacyId)){assert.equal(L.filterProducts('asp',new URLSearchParams({q:p.aliases[0]}))[0].id,p.id);assert.ok(L.isExact(p,p.aliases[0]));}
 assert.equal(byId('u02').name,'VOLTYN N36');assert.equal(byId('s02').family,'SVITRA');assert.equal(byId('c02').family,'STRUNEX');assert.equal(byId('u02').price,219000);
});

test('R1 inherited and unknown category keys are rejected in filters, URL context and restored state',()=>{
 for(const bad of ['__proto__','constructor','toString','not-a-category']) {
  assert.equal(L.isGroup(bad),false);
  assert.equal(L.normalizeGroup(bad),'ups');
  const url=new URL(`https://example.test/#/asp/catalog?cat=${encodeURIComponent(bad)}&f0=Cu`);
  const params=new URLSearchParams(url.hash.split('?')[1]);
  assert.equal(L.catalogCategory(params),null);
  assert.deepEqual(L.filterProducts('asp',params),[]);
  assert.deepEqual(L.filterProducts('ng',params),[]);
  const raw=JSON.parse(`{"cart":{"u02":3},"compareByGroup":{"ups":["u02"],"${bad}":["u01"]},"view":{"group":"${bad}","pairs":{"${bad}":["u01"]}},"catalogs":{"asp":"${url.hash}"}}`);
  const s=L.migrateState(raw);
  assert.equal(s.view.group,'ups');assert.equal(s.catalogs.asp,'');
  assert.deepEqual(s.cart,{u02:3});assert.deepEqual(s.compareByGroup.ups,['u02']);
  assert.deepEqual(Object.keys(s.compareByGroup),Object.keys(groups));
  assert.equal(L.moveComparison(s,bad,'u02',1),false);
  assert.deepEqual(L.readState({getItem:()=>JSON.stringify(raw)}).state,s);
 }
 for(const good of Object.keys(groups)) assert.equal(L.catalogCategory(new URLSearchParams({cat:good})),good);
 assert.equal(L.catalogCategory(new URLSearchParams()),'all');
 assert.equal(L.catalogCategory(new URLSearchParams({cat:'all'})),'all');
});
