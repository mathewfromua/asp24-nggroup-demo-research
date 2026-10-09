import type {Brand, GroupId, Product, DemoState} from './types.ts';
import {products, groups, GROUP_IDS} from '../data/catalog.ts';
import {inspectOrders, defaultCheckout, sanitizeCheckout} from '../../orders.js';
import {COMPARE_LIMIT, quantity, normalizeGroup, catalogCategory} from './common.ts';
import {record, uniqueStrings} from './validation.ts';
import {visiblePair} from './comparison.ts';
export function validRoute(value: unknown, catalogOnly = false): value is string {
  return typeof value === 'string' && value.length < 2000 && (catalogOnly ? /^#\/(asp|ng)\/catalog(?:\?[^#]*)?$/ : /^#\/(asp|ng)\/(?:(?:catalog|compare|cart|favorites|documents|partners|service|checkout|orders|projects|templates|lab|model-map)|(?:product|document|order|project|lab)\/[a-z0-9-]+)(?:\?[^#]*)?$/).test(value);
}
export function initialState(): DemoState {
  return {version: 4, science: {}, recovery: null, orders: [], checkout: defaultCheckout(), cart: {}, favorites: [], compareByGroup: Object.fromEntries(GROUP_IDS.map(g => [g, [] as string[]])) as Record<GroupId, string[]>, listName: 'Мій об’єкт', note: '', catalogs: {asp: '', ng: ''}, drafts: {}, view: {catalogViews: {asp: 'cards', ng: 'cards'}, comparisonDialog: null, group: 'ups', differences: false, expanded: false, compareBrand: 'asp', compareExperience: 'classic', research: Object.fromEntries(GROUP_IDS.map(g => [g, {scroll: 0, x: 0, row: '', offset: 0}])) as DemoState['view']['research'], pairs: Object.fromEntries(GROUP_IDS.map(g => [g, [] as string[]])) as Record<GroupId, string[]>, pages: {}}};
}
export function migrateState(raw: unknown, catalog: readonly Product[] = products): DemoState {
  const s = record(raw), result = initialState(), byId = (id: unknown) => catalog.find(p => p.id === id);
  result.cart = Object.fromEntries(Object.entries(record(s.cart)).filter((entry): entry is [string, number] => !!byId(entry[0])?.available && typeof entry[1] === 'number' && Number.isInteger(entry[1]) && quantity(entry[1]) !== null));
  const restored = inspectOrders(s.orders);
  result.orders = restored.orders;
  result.science = record(s.science);
  const oldRecovery = record(s.recovery);
  if (typeof oldRecovery.rawState === 'string') result.recovery = {version: 1, rawState: oldRecovery.rawState, quarantinedOrders: Array.isArray(oldRecovery.quarantinedOrders) ? oldRecovery.quarantinedOrders : []};
  if (restored.quarantined.length) result.recovery = {version: 1, rawState: result.recovery?.rawState || JSON.stringify(raw), quarantinedOrders: [...(result.recovery?.quarantinedOrders || []), ...restored.quarantined]};
  if (s.checkout) result.checkout = sanitizeCheckout(s.checkout);
  result.favorites = uniqueStrings(s.favorites).filter(id => byId(id));
  for (const group of GROUP_IDS) {
    const ids = Array.isArray(s.compare) ? s.compare : record(s.compareByGroup)[group];
    result.compareByGroup[group] = uniqueStrings(ids).filter(id => byId(id)?.group === group).slice(0, COMPARE_LIMIT);
  }
  if (typeof s.listName === 'string') result.listName = s.listName.slice(0, 100);
  if (typeof s.note === 'string') result.note = s.note.slice(0, 1000);
  for (const brand of ['asp', 'ng'] as const) { const url = record(s.catalogs)[brand]; if (validRoute(url, true) && url.startsWith(`#/${brand}/`) && catalogCategory(new URLSearchParams(url.split('?')[1] || '')) !== null) result.catalogs[brand] = url; }
  for (const [id, rawDraft] of Object.entries(record(s.drafts))) {
    if (!byId(id)?.ng) continue;
    const d = record(rawDraft);
    result.drafts[id] = {purpose: typeof d.purpose === 'string' && ['Сумісність', 'Партія', 'Тест'].includes(d.purpose) ? d.purpose : 'Сумісність', quantity: quantity(d.quantity) ? String(quantity(d.quantity)) : '', question: String(d.question ?? '').slice(0, 1500)};
  }
  const view = record(s.view);
  for (const brand of ['asp', 'ng'] as const) { const mode = record(view.catalogViews)[brand]; result.view.catalogViews[brand] = mode === 'family' ? 'series' : (mode === 'cards' || mode === 'list' || mode === 'series') ? mode : 'cards'; }
  const dialog = record(view.comparisonDialog);
  if (dialog.type === 'details' && typeof dialog.id === 'string' && byId(dialog.id)) result.view.comparisonDialog = {type: 'details', id: dialog.id};
  result.view.group = normalizeGroup(view.group);
  result.view.differences = view.differences === true;
  result.view.expanded = view.expanded === true;
  result.view.compareBrand = view.compareBrand === 'ng' ? 'ng' : 'asp';
  result.view.compareExperience = view.compareExperience === 'modern' ? 'modern' : 'classic';
  for (const group of GROUP_IDS) {
    const r = record(record(view.research)[group]);
    result.view.research[group] = {scroll: Math.max(0, Math.min(100000, Number(r.scroll) || 0)), x: Math.max(0, Math.min(10000, Number(r.x) || 0)), row: typeof r.row === 'string' ? r.row.slice(0, 200) : '', offset: Math.max(-1000, Math.min(1000, Number(r.offset) || 0))};
  }
  for (const group of GROUP_IDS) result.view.pairs[group] = visiblePair(result.compareByGroup[group], record(view.pairs)[group]);
  for (const [url, rawPage] of Object.entries(record(view.pages)).slice(-80)) {
    if (!validRoute(url)) continue;
    const p = record(rawPage);
    result.view.pages[url] = {scroll: Math.max(0, Math.min(100000, Number(p.scroll) || 0)), details: Array.isArray(p.details) ? p.details.slice(0, 10).map(Boolean) : [], focus: typeof p.focus === 'string' ? p.focus.slice(0, 300) : ''};
  }
  return result;
}
