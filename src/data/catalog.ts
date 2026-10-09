import {products as fixtureProducts, groups as fixtureGroups, display as legacyDisplay, money as legacyMoney, numericValue as legacyNumericValue, reelLength as legacyReelLength} from '../../data.js';
import type {GroupId, Product, ProductGroup} from '../domain/types.ts';
import {isRecord, hasUnsafeKeys} from '../domain/validation.ts';

export const CATALOG_SCHEMA_VERSION = 1;
export const GROUP_IDS: readonly GroupId[] = ['ups', 'optics', 'switches', 'cable', 'wifi', 'splitters', 'meters', 'injectors'];
export const isGroupId = (value: unknown): value is GroupId => typeof value === 'string' && (GROUP_IDS as readonly string[]).includes(value);
const scalar = (value: unknown): boolean => typeof value === 'string' || typeof value === 'boolean' || (typeof value === 'number' && Number.isFinite(value));
function parameter(value: unknown): boolean {
  if (value === null || scalar(value)) return true;
  if (!isRecord(value)) return false;
  if (value.status === 'known') return scalar(value.value) && (value.unit === undefined || typeof value.unit === 'string');
  if (['unknown', 'missing', 'not-applicable'].includes(String(value.status))) return value.reason === undefined || typeof value.reason === 'string';
  return value.status === 'conflicting' && Array.isArray(value.values) && value.values.length >= 2 && value.values.every(v => isRecord(v) && v.status === 'known' && parameter(v)) && (value.reason === undefined || typeof value.reason === 'string');
}
/** Validate the API/file boundary before the data becomes actionable. No SKU/name identity guesses. */
export function validateCatalog(value: unknown): asserts value is Product[] {
  if (!Array.isArray(value) || hasUnsafeKeys(value)) throw new Error('Некоректний список моделей.');
  const ids = new Set<string>();
  for (const item of value) {
    if (!isRecord(item) || typeof item.id !== 'string' || !/^[a-z0-9]+$/.test(item.id) || ids.has(item.id)) throw new Error('Неприпустимий або повторений stable ID моделі.');
    if (!isGroupId(item.group) || ['name','sku','code','manufacturer','family','typeLabel','unit','revision'].some(key => typeof item[key] !== 'string' || !String(item[key]).trim())) throw new Error(`Неповна ідентичність моделі ${item.id}.`);
    if (typeof item.price !== 'number' || !Number.isSafeInteger(item.price) || item.price < 0 || typeof item.available !== 'boolean' || typeof item.ng !== 'boolean') throw new Error(`Некоректна ціна або доступність ${item.id}.`);
    if (!isRecord(item.props) || !Object.values(item.props).every(parameter)) throw new Error(`Некоректні параметри ${item.id}.`);
    if (item.aliases !== undefined && (!Array.isArray(item.aliases) || !item.aliases.every(v => typeof v === 'string'))) throw new Error(`Некоректні псевдоніми ${item.id}.`);
    if (item.numericFacets !== undefined && (!isRecord(item.numericFacets) || !Object.values(item.numericFacets).every(v => isRecord(v) && (v.value === null || (typeof v.value === 'number' && Number.isFinite(v.value))) && typeof v.unit === 'string' && typeof v.derivedFrom === 'string'))) throw new Error(`Некоректні числові величини ${item.id}.`);
    if (item.unitDefinition !== undefined) {
      const u = item.unitDefinition;
      if (!isRecord(u) || u.integerOnly !== true || (item.group === 'cable' ? u.kind !== 'reel' || typeof u.lengthM !== 'number' || !Number.isFinite(u.lengthM) || u.lengthM <= 0 : u.kind !== 'piece')) throw new Error(`Некоректна одиниця продажу ${item.id}.`);
    }
    ids.add(item.id);
  }
}
export function parseCatalogJson(text: string): Product[] {
  const envelope: unknown = JSON.parse(text);
  if (!isRecord(envelope) || envelope.schemaVersion !== CATALOG_SCHEMA_VERSION || envelope.sourceKind !== 'synthetic-ui-fixture') throw new Error('Потрібен синтетичний каталог schemaVersion 1.');
  validateCatalog(envelope.products);
  return envelope.products;
}
export function validateGroups(value: unknown): asserts value is Record<GroupId, ProductGroup> {
  if (!isRecord(value) || Object.keys(value).length !== GROUP_IDS.length || hasUnsafeKeys(value)) throw new Error('Некоректні категорії каталогу.');
  for (const id of GROUP_IDS) {
    const g = value[id];
    if (!isRecord(g) || ['icon','label','description','name','typeLabel','family'].some(key => typeof g[key] !== 'string') || ['filters','keys'].some(key => !Array.isArray(g[key]) || !g[key].every((v: unknown) => typeof v === 'string')) || !Array.isArray(g.numericFacetDefinitions) || !g.numericFacetDefinitions.every(v => Array.isArray(v) && v.length === 3 && v.every(entry => typeof entry === 'string'))) throw new Error(`Некоректна категорія ${id}.`);
  }
}
// Once at the module boundary, not on every UI render. The hub never imports this module.
const checkedProducts: unknown = fixtureProducts;
const checkedGroups: unknown = fixtureGroups;
validateCatalog(checkedProducts);
validateGroups(checkedGroups);
export const products: Product[] = checkedProducts;
export const groups: Record<GroupId, ProductGroup> = checkedGroups;
export const display: (value: unknown) => string = legacyDisplay;
export const money: (cents: number) => string = legacyMoney;
export const numericValue: (product: Product, key: string) => number | null = legacyNumericValue;
export const reelLength: (product: Pick<Product, 'unit' | 'unitDefinition'>) => number | null = legacyReelLength;
export const byId = (id: string): Product | undefined => products.find(product => product.id === id);
