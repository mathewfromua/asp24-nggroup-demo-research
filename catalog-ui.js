import {products,groups,display,money,highlights} from './data.js';
import {filterProducts,isExact,catalogCategory,isGroup,modelCount,quantityLabel,plural} from './logic.js';
import {escapeHTML as esc,readable} from './presentation.js';

export const CATALOG_PAGE_SIZE=24;
const units={W:'Вт',Wh:'Вт·год',g:'г',Gbps:'Гбіт/с',km:'км',m:'м',count:'шт.'};
export function catalogPage(params,total) {
  const pages=Math.max(1,Math.ceil(total/CATALOG_PAGE_SIZE));
  const raw=params.get('page')||'1';
  const page=/^[1-9]\d{0,5}$/.test(raw)?Math.min(Number(raw),pages):1;
  return {page,pages,start:(page-1)*CATALOG_PAGE_SIZE,end:Math.min(page*CATALOG_PAGE_SIZE,total)};
}
export function renderCatalog(ctx) {
 const {route,state,productCard,compareButton,favoriteButton,cartButton,icon,empty,dock}=ctx;
 const cat=catalogCategory(route.params);
 if(cat===null)return empty('Категорію не знайдено','Оберіть групу обладнання.','До каталогу','clear-filters');
 const g=isGroup(cat)?groups[cat]:null,params=route.params,result=filterProducts(route.brand,params);
 const view=['cards','list','series'].includes(params.get('view'))?params.get('view'):(state.view.catalogViews?.[route.brand]||'cards');
 const available=products.filter(p=>(route.brand==='asp'||p.ng)&&(cat==='all'||p.group===cat));
 const paging=catalogPage(params,result.length),rows=result.slice(paging.start,paging.end);
 const link=p=>`#/${route.brand==='ng'&&!p.ng?'asp':route.brand}/product/${p.id}`;
 const list=items=>`<div class="technical-list">${items.map(p=>`<article class="technical-item" data-product-id="${p.id}"><div class="technical-title"><h3><a href="${link(p)}">${readable(p.name)}</a></h3>${cat==='all'?`<p>${esc(p.typeLabel||groups[p.group].name)}</p>`:''}<span class="mono">${p.sku}</span></div><dl>${highlights[p.group].map(k=>`<div><dt>${esc(k)}</dt><dd>${readable(display(p.props[k]))}</dd></div>`).join('')}</dl><div class="technical-offer"><strong>${money(p.price)}</strong><span>${quantityLabel(p,1)}</span><span class="stock ${p.available?'':'no'}">${p.available?'В наявності':'Немає в наявності'}</span></div><div class="technical-actions">${route.brand==='asp'?cartButton(p):`<a class="btn secondary" href="${link(p)}">Технічна картка</a>`}${compareButton(p)}${favoriteButton(p)}<button class="project-mini" data-action="comparison-save-to-project" data-ids="${p.id}" aria-label="Додати ${esc(p.name)} до проєкту">У проєкт</button></div></article>`).join('')}</div>`;
 const chipLabel=(k,v)=> k==='q'?`Пошук: ${v}`:k==='manufacturer'?`Виробник: ${v}`:k==='available'?'У наявності':k==='price_min'?`Ціна від ${v} грн`:k==='price_max'?`Ціна до ${v} грн`:k.startsWith('n_')?`${g?.numericFacetDefinitions.find(d=>k===`n_${d[0]}_min`||k===`n_${d[0]}_max`)?.[1]||'Параметр'} ${k.endsWith('_min')?'від':'до'} ${v}`:v;
 const chips=[];
 for(const [k,v] of params)if(['q','available','manufacturer','price_min','price_max'].includes(k)||/^f\d+$/.test(k)||k.startsWith('n_'))chips.push(`<span class="chip">${esc(chipLabel(k,v))}<button data-action="remove-filter" data-key="${esc(k)}" data-value="${esc(v)}" aria-label="Прибрати умову ${esc(v)}">×</button></span>`);
 const facet=(key,label,options,getValue,open=false)=>{
  const chosen=params.getAll(key),other=new URLSearchParams(params);other.delete(key);
  const matches=filterProducts(route.brand,other),counts=new Map();
  for(const p of matches){const v=getValue(p);counts.set(v,(counts.get(v)||0)+1);}
  return `<details class="facet" ${open||chosen.length?'open':''}><summary>${esc(label)}${chosen.length?` · ${chosen.length}`:''}</summary><div class="facet-options">${options.map(v=>{const count=counts.get(v)||0,on=chosen.includes(v);return `<label class="check ${!count&&!on?'facet-unavailable':''}"><input type="checkbox" data-multi-filter="${esc(key)}" value="${esc(v)}" ${on?'checked':''} ${!count&&!on?'disabled':''}><span>${readable(v)}</span><span class="facet-count" aria-label="${modelCount(count)}">${count}</span></label>`;}).join('')}</div></details>`;
 };
 const manufacturers=[...new Set(available.map(p=>p.manufacturer))].sort((a,b)=>a.localeCompare(b,'uk'));
 const brandFacet=facet('manufacturer','Виробник',manufacturers,p=>p.manufacturer,true);
 const filterMarkup=g?g.filters.map((key,i)=>facet('f'+i,key,[...new Set(available.map(p=>display(p.props[key])))].sort((a,b)=>a.localeCompare(b,'uk',{numeric:true})),p=>display(p.props[key]),i===0)).join(''):'<p class="filter-hint">Оберіть категорію для технічних параметрів.</p>';
 const rangeForm=(name,label,keyMin,keyMax)=>`<form class="range-form" data-catalog-range><span class="range-caption">${esc(label)}</span><div class="range-inputs"><label><span>Від</span><input type="number" step="any" min="0" name="${keyMin}" value="${esc(params.get(keyMin)||'')}" aria-label="${esc(label)}: від" inputmode="decimal"></label><label><span>До</span><input type="number" step="any" min="0" name="${keyMax}" value="${esc(params.get(keyMax)||'')}" aria-label="${esc(label)}: до" inputmode="decimal"></label></div><button class="text-btn" type="submit">Застосувати</button><p class="range-error" role="status"></p></form>`;
 const ranges=`<details class="facet" ${params.has('price_min')||params.has('price_max')?'open':''}><summary>Ціна, грн</summary>${rangeForm('price','Ціна, грн','price_min','price_max')}</details>`+(g?.numericFacetDefinitions||[]).map(([key,label,unit])=>`<details class="facet" ${params.has(`n_${key}_min`)||params.has(`n_${key}_max`)?'open':''}><summary>${esc(label)}: діапазон</summary>${rangeForm(key,`${label}, ${units[unit]||unit}`,`n_${key}_min`,`n_${key}_max`)}</details>`).join('');
 const sorts=[['','За відповідністю'],['price-up','Ціна: за зростанням'],['price-down','Ціна: за спаданням'],['name-up','Назва: А → Я'],['name-down','Назва: Я → А'],...(g?.numericFacetDefinitions||[]).flatMap(([key,label])=>[[key+'-up',label+': за зростанням'],[key+'-down',label+': за спаданням']])];
 let content='';
 if(view==='cards')content=`<div class="grid">${rows.map(p=>productCard(p,isExact(p,params.get('q')))).join('')}</div>`;
 else if(view==='list')content=list(rows);
 else {
  const families=new Map();for(const p of rows){const key=p.group+'|'+p.family;const f=families.get(key)||{name:p.family,group:p.group,rows:[]};f.rows.push(p);families.set(key,f);}
  content=[...families.values()].map(f=>`<details class="series-group" open><summary><span><strong>${esc(f.name)}</strong><small>${esc(groups[f.group].name)}</small></span><span>${modelCount(f.rows.length)} на цій сторінці</span></summary>${list(f.rows)}</details>`).join('');
 }
 const pageUrl=n=>{const next=new URLSearchParams(params);if(n===1)next.delete('page');else next.set('page',String(n));return `#/${route.brand}/catalog?${esc(next.toString())}`;};
 const pageNumbers=[...new Set([1,paging.page-1,paging.page,paging.page+1,paging.pages])].filter(n=>n>=1&&n<=paging.pages).sort((a,b)=>a-b);
 const pager=result.length>CATALOG_PAGE_SIZE?`<nav class="catalog-pagination" aria-label="Сторінки каталогу">${paging.page>1?`<a href="${pageUrl(paging.page-1)}" rel="prev">← Попередня</a>`:''}${pageNumbers.map((n,i)=>`${i&&n>pageNumbers[i-1]+1?'<span aria-hidden="true">…</span>':''}<a href="${pageUrl(n)}" ${n===paging.page?'aria-current="page"':''} aria-label="Сторінка ${n}">${n}</a>`).join('')}${paging.page<paging.pages?`<a href="${pageUrl(paging.page+1)}" rel="next">Наступна →</a>`:''}</nav>`:'';
 return `<div class="catalog-layout"><aside class="sidebar" aria-label="Категорії та фільтри"><details class="catalog-filter-panel" ${typeof matchMedia==='function'&&matchMedia('(max-width:700px)').matches?'':'open'}><summary class="filter-panel-heading">Категорії та фільтри</summary><div class="category-list">${[['all',{name:'Усе обладнання',icon:'grid'}],...Object.entries(groups)].map(([key,val])=>`<button data-action="category" data-key="${key}" class="${cat===key?'active':''}" aria-pressed="${cat===key}">${icon(val.icon)}<span>${esc(val.name)}</span><span class="count">${products.filter(p=>(route.brand==='asp'||p.ng)&&(key==='all'||p.group===key)).length}</span></button>`).join('')}</div><div class="filter-box"><label class="check stock-filter"><input type="checkbox" data-filter="available" ${params.get('available')?'checked':''}>Лише в наявності</label>${brandFacet}${filterMarkup}${ranges}</div></details></aside><section class="catalog-results" aria-label="Результати каталогу"><div class="results-top"><div><h1>${esc(g?.name||(route.brand==='ng'?'Технічний каталог':'Каталог обладнання'))}</h1><p class="result-count" role="status">${modelCount(result.length)}${result.length?` · показано ${paging.start+1}–${paging.end}`:''}</p></div><label class="sort-field"><span class="sr-only">Сортування</span><select aria-label="Сортування" data-filter="sort">${sorts.map(([value,label])=>`<option value="${value}" ${params.get('sort')===value?'selected':''}>${esc(label)}</option>`).join('')}</select></label></div><div class="catalog-viewbar"><div class="view-switch" role="group" aria-label="Подання каталогу">${[['cards','Картки'],['list','Список'],['series','Серії']].map(([key,label])=>`<button data-action="catalog-view" data-key="${key}" aria-pressed="${view===key}">${label}</button>`).join('')}</div>${g?`<a class="text-link" href="#/${route.brand}/model-map?${esc(params.toString())}">Ціна та параметр →</a>`:''}</div>${chips.length?`<div class="chips">${chips.join('')}<button class="reset-filters" data-action="clear-filters">Скинути умови</button></div>`:''}${result.length?content:empty('За цими умовами моделей немає','Змініть пошук або приберіть окрему умову.','Скинути умови','clear-filters')}${pager}<p class="catalog-note">Умовні виробники, моделі й ціни. Ілюстрації позначають тип обладнання, а не конкретне виконання.</p>${dock()}</section></div>`;
}
