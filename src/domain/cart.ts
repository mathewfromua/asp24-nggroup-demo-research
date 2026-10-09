import type {DemoState, Product, ConsultationDraft} from './types.ts';
import {products, money, reelLength} from '../data/catalog.ts';
import {plural} from './common.ts';
export const cartTotal = (cart: Record<string, number>, catalog: readonly Product[] = products) => Object.entries(cart).reduce((sum, [id, q]) => sum + (catalog.find(p => p.id === id)?.price || 0) * q, 0);
export const cartCount = (cart: Record<string, number>): number => Object.values(cart).reduce((sum, q) => sum + q, 0);
export const quantityLabel = (p: Product, q: number): string => { const length = reelLength(p); return p.group === 'cable' ? `${q} ${plural(q, 'бухта', 'бухти', 'бухт')}${length !== null ? ` · ${q * length} м` : ''}` : `${q} ${p.unit || 'шт.'}`; };
export function addCartItem(state: DemoState, id: string, catalog: readonly Product[] = products): 'unavailable' | 'limit' | 'ok' {
  const p = catalog.find(p => p.id === id);
  if (!p?.available) return 'unavailable';
  if ((state.cart[id] || 0) >= 999) return 'limit';
  state.cart[id] = (state.cart[id] || 0) + 1;
  return 'ok';
}
export function listText(state: DemoState, catalog: readonly Product[] = products): string {
  return ['ASP24 / NG Group — ДЕМОНСТРАЦІЙНИЙ СПИСОК', state.listName, 'Усі ціни й дані умовні. Нічого не замовлено.', '', ...Object.entries(state.cart).map(([id, q]) => {
    const p = catalog.find(p => p.id === id);
    if (!p) throw new Error('Невідома модель у списку.');
    return `${p.name} | ${p.sku} | ${quantityLabel(p, q)} | ${money(p.price)} / ${p.unit} | ${money(p.price * q)}`;
  }), '', `Разом: ${money(cartTotal(state.cart, catalog))}`, `Примітка: ${state.note || '—'}`].join('\n');
}
export function consultationText(p: Product, draft: ConsultationDraft): string {
  return ['ASP24 / NG Group — ЛОКАЛЬНИЙ ПРИКЛАД ЗАПИТУ', `${p.name} | ${p.sku} | виконання ${p.revision}`, `Мета: ${draft.purpose}`, `Кількість: ${draft.quantity || 'Не визначена'}`, draft.question.trim(), '', 'Нічого не надіслано. Умовна модель.'].join('\n');
}
