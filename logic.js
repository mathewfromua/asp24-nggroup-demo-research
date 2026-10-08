import { inspectOrders, defaultCheckout, sanitizeCheckout } from './orders.js';
import {products, groups, display, money, numericValue, reelLength} from './data.js';

export const COMPARE_LIMIT = 6;
export const STATE_KEY = 'perspective-demo-v1';
export const isGroup = value => typeof value === 'string' && Object.hasOwn(groups, value);
export const normalizeGroup = value => isGroup(value) ? value : 'ups';
export function catalogCategory(params) {
  const value = params.get('cat');
  return value == null || value === '' || value === 'all' ? 'all' : isGroup(value) ? value : null;
}
const record = v => v && typeof v === 'object' && !Array.isArray(v) ? v : {};
const unique = a => [...new Set(Array.isArray(a) ? a : [])];
export const plural = (n, one, few, many) => n % 100 >= 11 && n % 100 <= 14 ? many : n % 10 === 1 ? one : n % 10 >= 2 && n % 10 <= 4 ? few : many;
export const modelCount = n => `${n} ${plural(n, 'модель', 'моделі', 'моделей')}`;
export const quantity = value => /^\d+$/.test(String(value).trim()) && Number(value) >= 1 && Number(value) <= 999 ? Number(value) : null;
export const normalizeSearch = s => String(s ?? '').toLocaleLowerCase('uk').replace(/[\s\-–]/g, '');
export const isExact = (p, q) => !!q && [p.name, p.sku, ...(p.aliases || [])].some(s => normalizeSearch(s) === normalizeSearch(q));

// Formatting is normalized; units remain part of the value. Unknown ≠ zero ≠ false.
export function semantic(value) {
  if (value == null) return 'unknown';
  if (typeof value === 'boolean') return `boolean:${value}`;
  let text = String(value).trim().toLocaleLowerCase('uk').replace(/\s+/g, ' ');
  text = text.replace(/(\d) (?=\d{3}(?:\D|$))/g, '$1').replace(/\d+(?:[.,]\d+)?/g, n => String(Number(n.replace(',', '.'))));
  return `value:${text.replace(/\s*([/×·])\s*/g, '$1').replace(/(\d)\s+(?=[a-zа-яіїєґ])/g, '$1')}`;
}
export const differs = (ps, key) => new Set(ps.map(p => semantic(p.props[key]))).size > 1;
export const comparisonKeys = (ps, only = false) => ps.length && isGroup(ps[0].group) ? groups[ps[0].group].keys.filter(k => !only || differs(ps, k)) : [];

export function filterProducts(brand, params = new URLSearchParams(), catalog = products) {
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
export function validRoute(value, catalogOnly = false) {
  return typeof value === 'string' && value.length < 2000 && (catalogOnly ? /^#\/(asp|ng)\/catalog(?:\?[^#]*)?$/ : /^#\/(asp|ng)\/(?:(?:catalog|compare|cart|favorites|documents|partners|service|checkout|orders|projects|templates|lab|model-map)|(?:product|document|order|project|lab)\/[a-z0-9-]+)(?:\?[^#]*)?$/).test(value);
}
export function initialState() {
  return {version: 4, science: {}, recovery: null, orders: [], checkout: defaultCheckout(), cart: {}, favorites: [], compareByGroup: Object.fromEntries(Object.keys(groups).map(g => [g, []])), listName: 'Мій об’єкт', note: '', catalogs: {asp: '', ng: ''}, drafts: {}, view: {catalogViews: {asp: 'cards', ng: 'cards'}, comparisonDialog: null, group: 'ups', differences: false, expanded: false, compareBrand: 'asp', research: Object.fromEntries(Object.keys(groups).map(g => [g, {scroll: 0, x: 0, row: '', offset: 0}])), pairs: Object.fromEntries(Object.keys(groups).map(g => [g, []])), pages: {}}};
}
export function migrateState(raw, catalog = products) {
  const s = record(raw), result = initialState(), byId = id => catalog.find(p => p.id === id);
  result.cart = Object.fromEntries(Object.entries(record(s.cart)).filter(([id, q]) => byId(id)?.available && typeof q === 'number' && Number.isInteger(q) && quantity(q)));
  const restored = inspectOrders(s.orders);
  result.orders = restored.orders;
  result.science = record(s.science);
  const oldRecovery = record(s.recovery);
  if (typeof oldRecovery.rawState === 'string') result.recovery = {version: 1, rawState: oldRecovery.rawState, quarantinedOrders: Array.isArray(oldRecovery.quarantinedOrders) ? oldRecovery.quarantinedOrders : []};
  if (restored.quarantined.length) result.recovery = {version: 1, rawState: result.recovery?.rawState || JSON.stringify(raw), quarantinedOrders: [...(result.recovery?.quarantinedOrders || []), ...restored.quarantined]};
  if (s.checkout) result.checkout = sanitizeCheckout(s.checkout);
  result.favorites = unique(s.favorites).filter(id => byId(id));
  for (const group of Object.keys(groups)) {
    const ids = Array.isArray(s.compare) ? s.compare : record(s.compareByGroup)[group];
    result.compareByGroup[group] = unique(ids).filter(id => byId(id)?.group === group).slice(0, COMPARE_LIMIT);
  }
  if (typeof s.listName === 'string') result.listName = s.listName.slice(0, 100);
  if (typeof s.note === 'string') result.note = s.note.slice(0, 1000);
  for (const brand of ['asp', 'ng']) { const url = record(s.catalogs)[brand]; if (validRoute(url, true) && url.startsWith(`#/${brand}/`) && catalogCategory(new URLSearchParams(url.split('?')[1] || '')) !== null) result.catalogs[brand] = url; }
  for (const [id, rawDraft] of Object.entries(record(s.drafts))) {
    if (!byId(id)?.ng) continue;
    const d = record(rawDraft);
    result.drafts[id] = {purpose: ['Сумісність', 'Партія', 'Тест'].includes(d.purpose) ? d.purpose : 'Сумісність', quantity: quantity(d.quantity) ? String(quantity(d.quantity)) : '', question: String(d.question ?? '').slice(0, 1500)};
  }
  const view = record(s.view);
  for (const brand of ['asp', 'ng']) { const mode = record(view.catalogViews)[brand]; result.view.catalogViews[brand] = mode === 'family' ? 'series' : ['cards', 'list', 'series'].includes(mode) ? mode : 'cards'; }
  const dialog = record(view.comparisonDialog);
  if (dialog.type === 'details' && byId(dialog.id)) result.view.comparisonDialog = {type: 'details', id: dialog.id};
  result.view.group = normalizeGroup(view.group);
  result.view.differences = view.differences === true;
  result.view.expanded = view.expanded === true;
  result.view.compareBrand = view.compareBrand === 'ng' ? 'ng' : 'asp';
  for (const group of Object.keys(groups)) {
    const r = record(record(view.research)[group]);
    result.view.research[group] = {scroll: Math.max(0, Math.min(100000, Number(r.scroll) || 0)), x: Math.max(0, Math.min(10000, Number(r.x) || 0)), row: typeof r.row === 'string' ? r.row.slice(0, 200) : '', offset: Math.max(-1000, Math.min(1000, Number(r.offset) || 0))};
  }
  for (const group of Object.keys(groups)) result.view.pairs[group] = visiblePair(result.compareByGroup[group], record(view.pairs)[group]);
  for (const [url, rawPage] of Object.entries(record(view.pages)).slice(-80)) {
    if (!validRoute(url)) continue;
    const p = record(rawPage);
    result.view.pages[url] = {scroll: Math.max(0, Math.min(100000, Number(p.scroll) || 0)), details: Array.isArray(p.details) ? p.details.slice(0, 10).map(Boolean) : [], focus: typeof p.focus === 'string' ? p.focus.slice(0, 300) : ''};
  }
  return result;
}
export function readState(storage) {
  let raw;
  try { raw = storage.getItem(STATE_KEY); const parsed = raw ? JSON.parse(raw) : null; const state = migrateState(parsed); if (state.recovery && !record(parsed).recovery) state.recovery.rawState = raw; return {state, status: state.recovery ? 'recovery' : 'ok'}; }
  catch (error) { const state = initialState(); if (error instanceof SyntaxError && typeof raw === 'string') state.recovery = {version: 1, rawState: raw, quarantinedOrders: []}; return {state, status: error instanceof SyntaxError ? 'corrupt' : 'denied'}; }
}
export function writeState(storage, state) {
  try {
    let next = state;
    // A normal write must never erase unreadable historical orders. Explicit demo
    // reset may clear working records, but their recoverable source remains.
    if (!state.recovery && typeof storage.getItem === 'function') {
      const previous = readState(storage);
      if (previous.status === 'denied') return false;
      if (previous.state.recovery) next = {...state, recovery: previous.state.recovery};
    }
    storage.setItem(STATE_KEY, JSON.stringify(next)); return true;
  } catch { return false; }
}
export function visiblePair(ids, pair = []) {
  return [...new Set([...(Array.isArray(pair) ? pair : []).filter(id => ids.includes(id)), ...ids])].slice(0, 2);
}
export function selectPair(ids, pair, slot, id) {
  const next = visiblePair(ids, pair);
  if (!ids.includes(id)) return next;
  const other = slot === 0 ? 1 : 0;
  if (next[other] === id) next[other] = next[slot];
  next[slot] = id;
  return next;
}
export function toggleComparison(state, id, catalog = products) {
  const p = catalog.find(p => p.id === id);
  if (!p || !isGroup(p.group)) return 'unknown';
  const ids = state.compareByGroup[p.group];
  if (ids.includes(id)) state.compareByGroup[p.group] = ids.filter(x => x !== id);
  else if (ids.length >= COMPARE_LIMIT) return 'limit';
  else ids.push(id);
  state.view.group = p.group;
  state.view.pairs[p.group] = visiblePair(state.compareByGroup[p.group], state.view.pairs[p.group]);
  return 'ok';
}
export function moveComparison(state, group, id, delta) {
  if (!isGroup(group)) return false;
  const ids = state.compareByGroup[group], i = ids.indexOf(id), to = i + delta;
  if (i < 0 || to < 0 || to >= ids.length) return false;
  [ids[i], ids[to]] = [ids[to], ids[i]];
  return true;
}
// Adding is idempotent. Replacement is explicit and keeps the column and pair slot.
export function addComparison(state, id, replaceId = '', catalog = products) {
  const p = catalog.find(p => p.id === id);
  if (!p || !isGroup(p.group)) return 'unknown';
  const ids = state.compareByGroup[p.group];
  if (ids.includes(id)) return 'exists';
  if (replaceId) {
    const at = ids.indexOf(replaceId);
    if (at < 0) return 'unknown';
    ids[at] = id;
    state.view.pairs[p.group] = state.view.pairs[p.group].map(x => x === replaceId ? id : x);
  } else {
    if (ids.length >= COMPARE_LIMIT) return 'limit';
    ids.push(id);
  }
  state.view.group = p.group;
  state.view.pairs[p.group] = visiblePair(ids, state.view.pairs[p.group]);
  return 'ok';
}
export function removeComparison(state, id) {
  const group = Object.keys(groups).find(g => state.compareByGroup[g].includes(id));
  if (!group) return null;
  const ids = state.compareByGroup[group], at = ids.indexOf(id);
  const undo = {group, id, at, pair: [...state.view.pairs[group]]};
  state.compareByGroup[group] = ids.filter(x => x !== id);
  state.view.pairs[group] = visiblePair(state.compareByGroup[group], state.view.pairs[group]);
  return undo;
}
export function undoComparison(state, undo) {
  if (!undo || !isGroup(undo.group)) return false;
  const ids = state.compareByGroup[undo.group];
  if (ids.includes(undo.id) || ids.length >= COMPARE_LIMIT) return false;
  ids.splice(Math.min(undo.at, ids.length), 0, undo.id);
  state.view.pairs[undo.group] = visiblePair(ids, undo.pair);
  return true;
}
export const cartTotal = (cart, catalog = products) => Object.entries(cart).reduce((sum, [id, q]) => sum + (catalog.find(p => p.id === id)?.price || 0) * q, 0);
export const cartCount = cart => Object.values(cart).reduce((sum, q) => sum + q, 0);
export const quantityLabel = (p, q) => p.group === 'cable' ? `${q} ${plural(q, 'бухта', 'бухти', 'бухт')}${reelLength(p) !== null ? ` · ${q * reelLength(p)} м` : ''}` : `${q} ${p.unit || 'шт.'}`;
export function addCartItem(state, id, catalog = products) {
  const p = catalog.find(p => p.id === id);
  if (!p?.available) return 'unavailable';
  if ((state.cart[id] || 0) >= 999) return 'limit';
  state.cart[id] = (state.cart[id] || 0) + 1;
  return 'ok';
}
export function listText(state, catalog = products) {
  return ['ПЕРСПЕКТИВА — ДЕМОНСТРАЦІЙНИЙ СПИСОК', state.listName, 'Усі ціни й дані умовні. Нічого не замовлено.', '', ...Object.entries(state.cart).map(([id, q]) => {
    const p = catalog.find(p => p.id === id);
    return `${p.name} | ${p.sku} | ${quantityLabel(p, q)} | ${money(p.price)} / ${p.unit} | ${money(p.price * q)}`;
  }), '', `Разом: ${money(cartTotal(state.cart, catalog))}`, `Примітка: ${state.note || '—'}`].join('\n');
}
export function consultationText(p, draft) {
  return ['ПЕРСПЕКТИВА — ЛОКАЛЬНИЙ ПРИКЛАД ЗАПИТУ', `${p.name} | ${p.sku} | виконання ${p.revision}`, `Мета: ${draft.purpose}`, `Кількість: ${draft.quantity || 'Не визначена'}`, draft.question.trim(), '', 'Нічого не надіслано. Умовна модель.'].join('\n');
}
