import type {Brand, Product} from './types.ts';
import {products, groups, display, numericValue} from '../data/catalog.ts';
import {catalogCategory, isGroup, normalizeSearch, isExact} from './common.ts';
export function filterProducts(brand: Brand, params = new URLSearchParams(), catalog: readonly Product[] = products): Product[] {
  const q = params.get('q') || '', cat = catalogCategory(params);
  if (cat === null) return [];
  const g = isGroup(cat) ? groups[cat] : null;
  let result = catalog.filter(p => (brand === 'asp' || p.ng) && (cat === 'all' || p.group === cat));
  if (q) result = result.filter(p => normalizeSearch([p.name, p.sku, p.code, p.manufacturer, p.family, p.typeLabel, ...(p.aliases || []), groups[p.group].name].join(' ')).includes(normalizeSearch(q)));
  const manufacturers=params.getAll('manufacturer').filter(Boolean);
  if(manufacturers.length)result=result.filter(p=>manufacturers.includes(p.manufacturer));
  for(const boundary of ['min','max']){const raw=params.get(`price_${boundary}`);if(raw==null||raw.trim()==='')continue;const value=Number(raw.replace(',','.'));if(!Number.isFinite(value)||value<0)return [];const cents=Math.round(value*100);result=result.filter(p=>boundary==='min'?p.price>=cents:p.price<=cents);}
  if (g) {
    g.filters.forEach((key, i) => { const values = params.getAll('f' + i).filter(Boolean); if (values.length) result = result.filter(p => values.includes(display(p.props[key]))); });
    for (const [key] of g.numericFacetDefinitions) {
      for (const boundary of ['min', 'max']) {
        const raw = params.get(`n_${key}_${boundary}`);
        if (raw == null || raw.trim() === '') continue;
        const limit = Number(raw.replace(',', '.'));
        if (!Number.isFinite(limit)) return [];
        result = result.filter(p => {const value = numericValue(p, key); return value !== null && (boundary === 'min' ? value >= limit : value <= limit);});
      }
    }
  }
  if (params.get('available')) result = result.filter(p => p.available);
  result.sort((a, b) => Number(isExact(b, q)) - Number(isExact(a, q)));
  if (params.get('sort') === 'price-up') result.sort((a, b) => a.price - b.price);
  if (params.get('sort') === 'price-down') result.sort((a, b) => b.price - a.price);
  const sort = params.get('sort') || '';
  if(['name-up','name-down'].includes(sort))result.sort((a,b)=>a.name.localeCompare(b.name,'uk',{numeric:true})*(sort==='name-down'?-1:1));
  const numericSort = sort.match(/^(?:numeric:)?([a-zA-Z][a-zA-Z0-9]*)(?:-(up|down)|:(asc|desc))$/);
  if (g && numericSort && g.numericFacetDefinitions.some(([key]) => key === numericSort[1])) {
    const descending = numericSort[2] === 'down' || numericSort[3] === 'desc';
    result.sort((a, b) => {const av = numericValue(a,numericSort[1]), bv = numericValue(b,numericSort[1]); return av === null ? (bv === null ? 0 : 1) : bv === null ? -1 : (av - bv) * (descending ? -1 : 1);});
  }
  return result;
}
