import {isIsoTimestamp} from './validation.js';
/** Local demonstration orders. No request, payment, account or delivery integration. */
import { products, groups, money, reelLength } from './data.js';

export const ORDER_STAGES = Object.freeze([
  { id: 'created', label: 'Створено' },
  { id: 'confirmed', label: 'Підтверджено' },
  { id: 'packed', label: 'Підготовлено' },
  { id: 'shipped', label: 'Відправлено' },
  { id: 'completed', label: 'Завершено' },
]);
export const MAX_ORDERS = 100;
const object = v => v && typeof v === 'object' && !Array.isArray(v) ? v : {};
const clean = (v, n) => typeof v === 'string' ? v.trim().slice(0, n) : '';
const validQty = v => Number.isInteger(v) && v >= 1 && v <= 999;
const stamp = isIsoTimestamp;
const allowedStatus = v => v === 'cancelled' || ORDER_STAGES.some(s => s.id === v);
export const stageLabel = id => id === 'cancelled' ? 'Скасовано' : ORDER_STAGES.find(s => s.id === id)?.label || 'Невідомий етап';
export const defaultCheckout = () => ({ alias: 'Демо-покупець', delivery: 'pickup', payment: 'invoice', note: '' });
export function sanitizeCheckout(value) {
  const v = object(value);
  return { alias: clean(v.alias, 80), delivery: v.delivery === 'demo-delivery' ? 'demo-delivery' : 'pickup', payment: v.payment === 'demo-card' ? 'demo-card' : 'invoice', note: clean(v.note, 600) };
}
export const deliveryLabel = v => v === 'demo-delivery' ? 'Умовна доставка' : 'Самовивіз';
export const paymentLabel = v => v === 'demo-card' ? 'Демо-оплата карткою' : 'Умовний рахунок';
export function createOrderId(now = new Date(), random = globalThis.crypto?.randomUUID?.()) {
  if (!random) throw new Error('SECURE_RANDOM_UNAVAILABLE');
  return `demo-${now.toISOString().slice(0, 10).replaceAll('-', '')}-${random.replaceAll('-', '').slice(0, 12).toLowerCase()}`;
}
export function orderTotal(items) {
  return items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0);
}
export function createDemoOrder(state, rawCheckout, options = {}) {
  const catalog = options.catalog || products;
  const checkout = sanitizeCheckout(rawCheckout);
  if (!checkout.alias) throw new Error('ALIAS_REQUIRED');
  const entries = Object.entries(object(state.cart));
  if (!entries.length) throw new Error('EMPTY_CART');
  if ((state.orders || []).length >= MAX_ORDERS) throw new Error('ORDER_LIMIT');
  const items = entries.map(([id, q]) => {
    const p = catalog.find(p => p.id === id);
    if (!p || !p.available) throw new Error('UNAVAILABLE_ITEM');
    if (!validQty(q) || !Number.isSafeInteger(p.price) || p.price < 0) throw new Error('INVALID_ITEM');
    const unitDefinition = p.group === 'cable' ? {kind: 'reel', lengthM: reelLength(p), integerOnly: true} : {kind: 'piece', integerOnly: true};
    return { productId: p.id, sku: p.sku, name: p.name, group: p.group, unit: p.unit, unitDefinition, availabilityState: p.availabilityState || (p.available ? 'available' : 'unavailable'), quantity: q, unitPrice: p.price };
  });
  const now = options.now || new Date().toISOString();
  if (!stamp(now)) throw new Error('INVALID_DATE');
  const id = options.id || createOrderId(new Date(now));
  if (!/^demo-[a-z0-9-]{8,60}$/.test(id)) throw new Error('INVALID_ID');
  if ((state.orders || []).some(o => o.id === id)) throw new Error('DUPLICATE_ID');
  const total = orderTotal(items);
  if (!Number.isSafeInteger(total)) throw new Error('TOTAL_OVERFLOW');
  return { id, createdAt: now, currency: 'UAH', localOnly: true, status: 'created', checkout, project: clean(state.listName, 100), items, total, history: [{ status: 'created', at: now }] };
}
export function transitionOrder(order, action, now = new Date().toISOString()) {
  if (!stamp(now) || !order || !allowedStatus(order.status)) return null;
  if (Date.parse(now) < Date.parse(order.history.at(-1).at)) return null;
  let next;
  if (action === 'cancel') {
    if (!['created', 'confirmed', 'packed'].includes(order.status)) return null;
    next = 'cancelled';
  } else if (action === 'next') {
    const at = ORDER_STAGES.findIndex(s => s.id === order.status);
    if (at < 0 || at >= ORDER_STAGES.length - 1) return null;
    next = ORDER_STAGES[at + 1].id;
  } else return null;
  return { ...order, status: next, history: [...order.history, { status: next, at: now }] };
}
/** Treat browser storage as untrusted. Keep valid immutable snapshots, recompute totals. */
export function restoreOrders(raw) {
  if (!Array.isArray(raw)) return [];
  const seen = new Set(), restored = [];
  for (const entry of raw.slice(0, MAX_ORDERS)) {
    const v = object(entry);
    if (typeof v.id !== 'string' || !/^demo-[a-z0-9-]{8,60}$/.test(v.id) || seen.has(v.id) || !stamp(v.createdAt) || !allowedStatus(v.status) || !Array.isArray(v.items) || !v.items.length || v.items.length > 100) continue;
    const ids = new Set(), items = [];
    let invalid = false;
    for (const rawItem of v.items) {
      const i = object(rawItem);
      if (typeof i.productId !== 'string' || !/^[a-z0-9]+$/.test(i.productId) || ids.has(i.productId) || !validQty(i.quantity) || !Number.isSafeInteger(i.unitPrice) || i.unitPrice < 0 || i.unitPrice > 1000000000 || !clean(i.name, 120) || !clean(i.sku, 80) || !Object.hasOwn(groups, i.group) || !clean(i.unit, 80)) { invalid = true; break; }
      ids.add(i.productId);
      const item = { productId: i.productId, sku: clean(i.sku, 80), name: clean(i.name, 120), group: i.group, unit: i.unit, quantity: i.quantity, unitPrice: i.unitPrice };
      if (i.unitDefinition !== undefined) {
        const u = object(i.unitDefinition);
        if (u.integerOnly !== true || (i.group === 'cable' ? u.kind !== 'reel' || typeof u.lengthM !== 'number' || !Number.isFinite(u.lengthM) || u.lengthM <= 0 || u.lengthM > 100000 : u.kind !== 'piece')) {invalid = true; break;}
        item.unitDefinition = i.group === 'cable' ? {kind: 'reel', lengthM: u.lengthM, integerOnly: true} : {kind: 'piece', integerOnly: true};
      }
      if (typeof i.availabilityState === 'string') item.availabilityState = clean(i.availabilityState, 40);
      items.push(item);
    }
    if (invalid || !Number.isSafeInteger(orderTotal(items))) continue;
    if (!Array.isArray(v.history) || !v.history.length || v.history.length > 6) continue;
    const history = [];
    for (let at = 0; at < v.history.length; at++) {
      const h = object(v.history[at]), prev = history.at(-1);
      if (!stamp(h.at) || !allowedStatus(h.status) || (at === 0 && (h.status !== 'created' || h.at !== v.createdAt))) { invalid = true; break; }
      if (prev) {
        const expected = transitionOrder({ status: prev.status, history: [prev] }, h.status === 'cancelled' ? 'cancel' : 'next', h.at);
        if (!expected || expected.status !== h.status) { invalid = true; break; }
      }
      history.push({ status: h.status, at: h.at });
    }
    if (invalid || history.at(-1)?.status !== v.status) continue;
    seen.add(v.id);
    restored.push({ id: v.id, createdAt: v.createdAt, currency: 'UAH', localOnly: true, status: v.status, checkout: sanitizeCheckout(v.checkout), project: clean(v.project, 100), items, total: orderTotal(items), history });
  }
  return restored;
}
/** Recovery is explicit: rejected records stay outside actionable order history. */
export function inspectOrders(raw) {
  if (raw === undefined || raw === null) return {orders: [], quarantined: []};
  if (!Array.isArray(raw)) return {orders: [], quarantined: [{index: null, reason: 'invalid-order-list', raw}]};
  const orders = [], quarantined = [], seen = new Set();
  raw.forEach((entry, index) => {
    const record = restoreOrders([entry])[0];
    const reason = index >= MAX_ORDERS ? 'order-limit' : !record ? 'invalid-order-record' : seen.has(record.id) ? 'duplicate-order-id' : '';
    if (reason) quarantined.push({index, reason, raw: entry});
    else {orders.push(record); seen.add(record.id);}
  });
  return {orders, quarantined};
}
export function repeatOrder(cart, order, catalog = products) {
  const next = { ...cart }, skipped = [], clamped = [], renamed = [], changedStatus = [];
  for (const item of order.items) {
    const p = catalog.find(p => p.id === item.productId);
    if (p && p.name !== item.name) renamed.push({id: p.id, from: item.name, to: p.name});
    const currentStatus = p ? p.availabilityState || (p.available ? 'available' : 'unavailable') : 'missing';
    const originalStatus = item.availabilityState || 'available';
    if (currentStatus !== originalStatus || !p?.available) changedStatus.push({id: item.productId, sku: item.sku, from: originalStatus, to: currentStatus});
    if (!p?.available) { skipped.push(item.sku); continue; }
    const q = (validQty(next[p.id]) ? next[p.id] : 0) + item.quantity;
    next[p.id] = Math.min(999, q);
    if (q > 999) clamped.push(item.sku);
  }
  return { cart: next, skipped, clamped, renamed, changedStatus };
}
export function orderText(order) {
  return ['ПЕРСПЕКТИВА — ДЕМОЗАМОВЛЕННЯ', order.id.toUpperCase(),
    'Лише локальна демонстрація. Нічого не надіслано, не оплачено й не зарезервовано.',
    `Створено: ${order.createdAt}`, `Етап симуляції: ${stageLabel(order.status)}`,
    `Псевдонім: ${order.checkout.alias}`, `Об’єкт: ${order.project || '—'}`,
    `Отримання: ${deliveryLabel(order.checkout.delivery)} (демо)`, `Оплата: ${paymentLabel(order.checkout.payment)} (без оплати)`, '',
    ...order.items.map(i => `${i.name} | ${i.sku} | ${i.quantity} × ${i.unit}${i.group === 'cable' && reelLength(i) !== null ? ` · ${i.quantity * reelLength(i)} м` : ''} | ${money(i.unitPrice)} | ${money(i.unitPrice * i.quantity)}`),
    '', `Разом: ${money(order.total)}`, 'Доставка й оплата не розраховуються та не виконуються.',
    `Примітка: ${order.checkout.note || '—'}`, '', 'ІСТОРІЯ СИМУЛЯЦІЇ',
    ...order.history.map(h => `${h.at} — ${stageLabel(h.status)}`)].join('\n');
}
