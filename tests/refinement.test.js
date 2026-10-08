import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {products,groups,byId,numericValue,reelLength} from '../data.js';
import {filterProducts,initialState,quantityLabel} from '../logic.js';
import {renderCatalog,catalogPage,CATALOG_PAGE_SIZE} from '../catalog-ui.js';
import {safeReferenceUrl,normalizeScience,createProject,validateProject,handleScience} from '../science.js';
import {isIsoTimestamp} from '../validation.js';
import {inspectOrders,createDemoOrder} from '../orders.js';
const baseline=JSON.parse(readFileSync(new URL('../evidence/refinement-20261008/catalog-before.json',import.meta.url)));

test('R01: all 64 pre-existing records preserve IDs, aliases, prices, units, properties and availability',()=>{
 for(const old of baseline.products)for(const key of ['id','name','sku','code','group','price','available','props','unit','unitDefinition','aliases','ng','revision'])assert.deepEqual(byId(old.id)[key],old[key],old.id+' '+key);
});
test('R02: 384 synthetic models, 13 manufacturers and at least six manufacturers in every category',()=>{
 assert.equal(products.length,384);assert.equal(new Set(products.map(p=>p.manufacturer)).size,13);
 for(const group of Object.keys(groups)){const rows=products.filter(p=>p.group===group);assert.ok(rows.length>=32);assert.ok(new Set(rows.map(p=>p.manufacturer)).size>=6);assert.ok(rows.some(p=>p.available));assert.ok(rows.some(p=>!p.available));}
 assert.ok(products.every(p=>p.isDemo&&p.sourceKind==='synthetic-ui-fixture'));
});
test('R03: manufacturers are OR, product facets remain AND, queries search manufacturer names',()=>{
 const params=new URLSearchParams('cat=ups&manufacturer=KRYNET&manufacturer=OBRYS&available=1');
 const rows=filterProducts('asp',params);assert.ok(rows.length>2);assert.ok(rows.every(p=>p.group==='ups'&&p.available&&['KRYNET','OBRYS'].includes(p.manufacturer)));
 params.set('f0','36 Вт');assert.ok(filterProducts('asp',params).every(p=>p.props['Потужність']==='36 Вт'));
 assert.ok(filterProducts('asp',new URLSearchParams('q=KRYNET')).every(p=>p.manufacturer==='KRYNET'));
});
test('R04: price ranges use currency cents, inclusive bounds, invalid values produce no false match',()=>{
 for(const group of Object.keys(groups)){const rows=filterProducts('asp',new URLSearchParams({cat:group,price_min:'1000',price_max:'5000'}));assert.ok(rows.every(p=>p.price>=100000&&p.price<=500000));}
 assert.deepEqual(filterProducts('asp',new URLSearchParams('price_min=bad')),[]);
 assert.deepEqual(filterProducts('asp',new URLSearchParams('price_min=5000&price_max=1000')),[]);
});
test('R05: pagination bounds and 24-result windows do not change the total candidate set',()=>{
 assert.equal(CATALOG_PAGE_SIZE,24);assert.deepEqual(catalogPage(new URLSearchParams(),384),{page:1,pages:16,start:0,end:24});
 assert.equal(catalogPage(new URLSearchParams('page=999'),48).page,2);assert.equal(catalogPage(new URLSearchParams('page=-1'),48).page,1);
 assert.equal(filterProducts('asp',new URLSearchParams('page=2')).length,384);
});
test('R06: name sorting is numeric-aware and explicitly selected price sorting stays monotonic',()=>{
 for(const sort of ['price-up','price-down']){const rows=filterProducts('asp',new URLSearchParams({sort}));assert.ok(rows.every((p,i)=>!i||(sort==='price-up'?p.price>=rows[i-1].price:p.price<=rows[i-1].price)));}
 const rows=filterProducts('asp',new URLSearchParams('sort=name-up'));assert.equal(rows.length,384);for(let i=1;i<rows.length;i++)assert.ok(rows[i-1].name.localeCompare(rows[i].name,'uk',{numeric:true})<=0);
});
test('R07: every numeric facet is finite or explicit null; cable length matches physical unit everywhere',()=>{
 for(const p of products){assert.ok(Number.isSafeInteger(p.price)&&p.price>0);assert.equal(p.numericFacets.priceCents.value,p.price);for(const facet of Object.values(p.numericFacets))assert.ok(facet.value===null||Number.isFinite(facet.value));if(p.group==='cable'){assert.equal(reelLength(p),p.unitDefinition.lengthM);assert.ok(quantityLabel(p,2).includes(String(2*reelLength(p))+' м'));}}
});
test('R08: new injector budget never exceeds sum of ports; no fabricated battery runtime',()=>{
 for(const p of products.filter(p=>!baseline.products.some(b=>b.id===p.id))){if(p.group==='injectors')assert.ok(numericValue(p,'budgetW')<=numericValue(p,'ports')*numericValue(p,'portMaxW')+1e-8);if(p.group==='ups'){assert.ok(numericValue(p,'energyWh')>0);assert.ok(!/годин автоном/i.test(p.desc));}}
});
test('R09: document references require a real model and the corresponding NG resource',()=>{
 assert.equal(safeReferenceUrl('#/ng/document/u02'),true);assert.equal(safeReferenceUrl('#/ng/document/s01'),false);assert.equal(safeReferenceUrl('#/asp/document/u02'),false);assert.equal(safeReferenceUrl('#/asp/product/s01'),true);assert.equal(safeReferenceUrl('#/ng/product/s01'),false);
 assert.equal(safeReferenceUrl('javascript:alert(1)'),false);assert.equal(safeReferenceUrl('https://example.com/file.pdf'),true);
});
test('R10: strict date validation rejects invalid calendars and attribute-like tails',()=>{
 assert.ok(isIsoTimestamp('2026-10-08T15:00:00.000Z'));
 for(const value of ['2026-02-30T00:00:00.000Z','2026-10-08T15:00:00Z','2026-10-08T15:00:00.000Z" autofocus="true','October 8, 2026'])assert.equal(isIsoTimestamp(value),false,value);
});
test('R11: an invalid historic order is quarantined while the original valid snapshot is preserved',()=>{
 const s=initialState();s.cart={u02:3};const o=createDemoOrder(s,{alias:'Демо'},{id:'demo-20261008-abcdef012345',now:'2026-10-08T15:00:00.000Z'});
 const r=inspectOrders([o,{...o,id:'demo-20261008-012345abcdef',createdAt:'2026-02-30T00:00:00.000Z'}]);assert.equal(r.orders.length,1);assert.equal(r.quarantined.length,1);assert.deepEqual(r.orders[0],o);
});
test('R12: map addition triggers a view refresh after the shared comparison changes',()=>{
 const state={...initialState(),science:normalizeScience()};let renders=0;
 handleScience('science-map-compare',{id:'u02'},state,{save:()=>true,render:()=>renders++,toast:()=>{},setComparison:(ids,g)=>{state.compareByGroup[g]=ids;return true;}});
 assert.equal(renders,1);assert.deepEqual(state.compareByGroup.ups,['u02']);
});
test('R13: changing the manufacturer retains different product types rather than category-labelled brands only',()=>{
 for(const name of ['KRYNET','OBRYS','TYVRA','DOVRIX','LUNETRA']){const rows=filterProducts('asp',new URLSearchParams({manufacturer:name}));assert.equal(new Set(rows.map(p=>p.group)).size,8);}
});
test('R14: large catalogue markup is paginated and the chart remains a separate contextual action',()=>{
 let rendered=[];const html=renderCatalog({route:{brand:'asp',params:new URLSearchParams()},state:initialState(),productCard:p=>{rendered.push(p.id);return '<article></article>';},compareButton:()=>'',favoriteButton:()=>'',cartButton:()=>'',icon:()=>'',empty:()=>'',dock:()=>''});
 assert.equal(rendered.length,24);assert.match(html,/384 моделі/);assert.match(html,/Сторінка 16/);assert.ok(!html.includes('Готові сценарії'));
});
