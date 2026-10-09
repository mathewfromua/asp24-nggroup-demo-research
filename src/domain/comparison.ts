import type {DemoState, GroupId, Product, ComparisonUndo, ParameterValue, KnownParameter} from './types.ts';
import {products, groups} from '../data/catalog.ts';
import {COMPARE_LIMIT, isGroup} from './common.ts';
// Formatting is normalized; units remain part of the value. Unknown ≠ zero ≠ false.
export function semantic(value: unknown): string {
  if (value == null) return 'unknown';
  if (typeof value === 'boolean') return `boolean:${value}`;
  let text = String(value).trim().toLocaleLowerCase('uk').replace(/\s+/g, ' ');
  text = text.replace(/(\d) (?=\d{3}(?:\D|$))/g, '$1').replace(/\d+(?:[.,]\d+)?/g, n => String(Number(n.replace(',', '.'))));
  return `value:${text.replace(/\s*([/×·])\s*/g, '$1').replace(/(\d)\s+(?=[a-zа-яіїєґ])/g, '$1')}`;
}
// A gap does not prove inequality; a row can also contain both at once.
export function comparisonStatus(ps: readonly Product[], key: string): {different: boolean; incomplete: boolean} {
  const values = ps.map(p => productParameter(p, key));
  const comparable = values.flatMap(value => value.status === 'known' ? [knownSemantic(value)] : value.status === 'not-applicable' ? ['not-applicable'] : []);
  return {different: new Set(comparable).size > 1, incomplete: values.some(value => value.status === 'unknown' || value.status === 'missing' || value.status === 'conflicting')};
}
export const differs = (ps: readonly Product[], key: string): boolean => comparisonStatus(ps, key).different;
export const comparisonKeys = (ps: readonly Product[], only = false): string[] => ps.length && isGroup(ps[0].group) && ps.every(p => p.group === ps[0].group) ? groups[ps[0].group].keys.filter(k => !only || (ps.length > 1 && Object.values(comparisonStatus(ps, k)).some(Boolean))) : [];

export function visiblePair(ids: readonly string[], pair: unknown = []): string[] {
  return [...new Set([...(Array.isArray(pair) ? pair : []).filter(id => ids.includes(id)), ...ids])].slice(0, 2);
}
export function selectPair(ids: readonly string[], pair: readonly string[], slot: number, id: string): string[] {
  const next = visiblePair(ids, pair);
  if (!ids.includes(id)) return next;
  const other = slot === 0 ? 1 : 0;
  if (next[other] === id) next[other] = next[slot];
  next[slot] = id;
  return next;
}
export function toggleComparison(state: DemoState, id: string, catalog: readonly Product[] = products): 'unknown' | 'limit' | 'ok' {
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
export function moveComparison(state: DemoState, group: unknown, id: string, delta: number): boolean {
  if (!isGroup(group)) return false;
  const ids = state.compareByGroup[group], i = ids.indexOf(id), to = i + delta;
  if (i < 0 || to < 0 || to >= ids.length) return false;
  [ids[i], ids[to]] = [ids[to], ids[i]];
  return true;
}
// Adding is idempotent. Replacement is explicit and keeps the column and pair slot.
export function addComparison(state: DemoState, id: string, replaceId = '', catalog: readonly Product[] = products): 'unknown' | 'exists' | 'limit' | 'ok' {
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
export function removeComparison(state: DemoState, id: string): ComparisonUndo | null {
  const group = (Object.keys(groups) as GroupId[]).find(g => state.compareByGroup[g].includes(id));
  if (!group) return null;
  const ids = state.compareByGroup[group], at = ids.indexOf(id);
  const undo = {group, id, at, pair: [...state.view.pairs[group]]};
  state.compareByGroup[group] = ids.filter(x => x !== id);
  state.view.pairs[group] = visiblePair(state.compareByGroup[group], state.view.pairs[group]);
  return undo;
}
export function undoComparison(state: DemoState, undo: ComparisonUndo | null): boolean {
  if (!undo || !isGroup(undo.group)) return false;
  const ids = state.compareByGroup[undo.group];
  if (ids.includes(undo.id) || ids.length >= COMPARE_LIMIT) return false;
  ids.splice(Math.min(undo.at, ids.length), 0, undo.id);
  state.view.pairs[undo.group] = visiblePair(ids, undo.pair);
  return true;
}

/** Missing key, explicit unknown, zero, false and not applicable have distinct meanings. */
export function productParameter(product: Product, key: string): ParameterValue {
  if (!Object.hasOwn(product.props, key) || product.props[key] === undefined) return {status: 'missing'};
  const value = product.props[key];
  if (value === null) return {status: 'unknown'};
  if (typeof value === 'object') return value;
  return {status: 'known', value};
}
export function parameterText(value: ParameterValue): string {
  if (value.status === 'known') return `${String(value.value)}${value.unit ? ` ${value.unit}` : ''}`;
  if (value.status === 'conflicting') return `Суперечливі дані: ${value.values.map(parameterText).join(' / ')}${value.reason ? ` — ${value.reason}` : ''}`;
  const label = value.status === 'missing' ? 'Параметр відсутній у джерелі' : value.status === 'not-applicable' ? 'Не застосовується' : 'Не уточнено';
  return `${label}${value.reason ? ` — ${value.reason}` : ''}`;
}
function knownSemantic(value: KnownParameter): string {
  return semantic(value.unit ? `${String(value.value)} ${value.unit}` : value.value);
}
export interface ComparisonRow {
  key: string; label: string;
  cells: {productId: string; value: ParameterValue; text: string}[];
  different: boolean; incomplete: boolean; conflicting: boolean;
}
export function comparisonRows(ps: readonly Product[], onlyDifferences = false): ComparisonRow[] {
  if (!ps.length || !isGroup(ps[0].group) || ps.some(p => p.group !== ps[0].group)) return [];
  return groups[ps[0].group].keys.map(key => {
    const cells = ps.map(p => {const value = productParameter(p, key); return {productId: p.id, value, text: parameterText(value)};});
    return {key, label: key, cells, ...comparisonStatus(ps, key),
      conflicting: cells.some(({value}) => value.status === 'conflicting')};
  }).filter(row => !onlyDifferences || (ps.length > 1 && (row.different || row.incomplete || row.conflicting)));
}
