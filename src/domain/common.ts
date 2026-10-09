import type {Product, GroupId} from './types.ts';
import {groups, isGroupId} from '../data/catalog.ts';
export const COMPARE_LIMIT = 6;
export const STATE_KEY = 'perspective-demo-v1';
export const isGroup = isGroupId;
export const normalizeGroup = (value: unknown): GroupId => isGroup(value) ? value : 'ups';
export function catalogCategory(params: URLSearchParams): GroupId | 'all' | null {
  const value = params.get('cat');
  return value == null || value === '' || value === 'all' ? 'all' : isGroup(value) ? value : null;
}
export const plural = (n: number, one: string, few: string, many: string) => n % 100 >= 11 && n % 100 <= 14 ? many : n % 10 === 1 ? one : n % 10 >= 2 && n % 10 <= 4 ? few : many;
export const modelCount = (n: number): string => `${n} ${plural(n, 'модель', 'моделі', 'моделей')}`;
export const quantity = (value: unknown): number | null => /^\d+$/.test(String(value).trim()) && Number(value) >= 1 && Number(value) <= 999 ? Number(value) : null;
export const normalizeSearch = (s: unknown): string => String(s ?? '').toLocaleLowerCase('uk').replace(/[\s\-–]/g, '');
export const isExact = (p: Product, q: string): boolean => !!q && [p.name, p.sku, ...(p.aliases || [])].some(s => normalizeSearch(s) === normalizeSearch(q));
