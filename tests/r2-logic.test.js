// Intended location: tests/r2-logic.test.js. Fixtures never enter the public catalog.
import test from 'node:test';
import assert from 'node:assert/strict';
import {products, groups, byId} from '../data.js';
import * as L from '../logic.js';

const ups = products.filter(p => p.group === 'ups').slice(0,6).map(p => p.id);
const seventh = {...byId('u01'), id: 'test-r2-seventh', sku: 'TEST-R2-7'};
const catalog = [...products, seventh];
const snapshot = state => JSON.stringify(state);
function selection(ids = ups) {
  const state = L.initialState();
  ids.forEach(id => assert.equal(L.addComparison(state, id, '', catalog), 'ok'));
  state.compareByGroup.optics = ['o01', 'o03'];
  state.view.pairs.optics = ['o03', 'o01'];
  state.view.pairs.ups = L.visiblePair(ids, ['u02', 'u04']);
  state.view.differences = true;
  state.cart = {u02: 3};
  state.drafts.u02 = {purpose: 'Тест', quantity: '', question: 'Перевірити модель'};
  return state;
}
const independent = state => ({
  optics: state.compareByGroup.optics,
  opticsPair: state.view.pairs.optics,
  cart: state.cart,
  drafts: state.drafts,
  differences: state.view.differences
});

test('R2 adding a selected candidate is idempotent, even with an explicit replacement target', () => {
  const state = selection(['u01', 'u02', 'u04']);
  state.view.group = 'optics';
  const before = snapshot(state);
  for (const replace of ['', 'u01', 'u04', 'missing']) {
    assert.equal(L.addComparison(state, 'u02', replace), 'exists');
    assert.equal(snapshot(state), before, `selected u02 must not remove itself or ${replace}`);
  }
});

test('R2 seventh fixture cannot silently evict a candidate; explicit replacement keeps every column and pair slot', () => {
  assert.equal(products.length, 384);
  assert.equal(products.some(p => p.id === seventh.id), false);
  const full = selection();
  const before = snapshot(full);
  assert.equal(L.addComparison(full, seventh.id, '', catalog), 'limit');
  assert.equal(snapshot(full), before);

  for (const replaced of ups) {
    for (const first of ups) for (const second of ups.filter(id => id !== first)) {
      const state = selection();
      state.view.pairs.ups = [first, second];
      const preserved = structuredClone(independent(state));
      assert.equal(L.addComparison(state, seventh.id, replaced, catalog), 'ok');
      assert.deepEqual(state.compareByGroup.ups, ups.map(id => id === replaced ? seventh.id : id));
      assert.deepEqual(state.view.pairs.ups, [first, second].map(id => id === replaced ? seventh.id : id));
      assert.equal(new Set(state.compareByGroup.ups).size, L.COMPARE_LIMIT);
      assert.deepEqual(independent(state), preserved);
    }
  }
});

test('R2 explicit replacement below the limit swaps in place and rejects wrong targets without any mutation', () => {
  const initial = ['u01', 'u02', 'u04'];
  for (const replaced of initial) {
    const state = selection(initial);
    assert.equal(L.addComparison(state, 'u06', replaced), 'ok');
    assert.deepEqual(state.compareByGroup.ups, initial.map(id => id === replaced ? 'u06' : id));
    assert.equal(state.compareByGroup.ups.length, initial.length);
  }
  for (const [id, target] of [['u06', 'missing'], ['u06', 'o01'], ['missing', 'u01']]) {
    const state = selection(initial), before = snapshot(state);
    assert.equal(L.addComparison(state, id, target), 'unknown');
    assert.equal(snapshot(state), before);
  }
});

test('R2 all removal positions undo to the same order and ordered pair; repeated undo has no effect', () => {
  for (const id of ups) {
    const state = selection(), original = structuredClone(state);
    const token = L.removeComparison(state, id);
    assert.equal(token.id, id);
    assert.equal(token.at, ups.indexOf(id));
    assert.deepEqual(state.compareByGroup.ups, ups.filter(value => value !== id));
    assert.ok(state.view.pairs.ups.every(value => state.compareByGroup.ups.includes(value)));
    assert.equal(new Set(state.view.pairs.ups).size, 2);
    assert.deepEqual(independent(state), independent(original));
    assert.equal(L.undoComparison(state, token), true);
    assert.deepEqual(state, original);
    const restored = snapshot(state);
    assert.equal(L.undoComparison(state, token), false);
    assert.equal(snapshot(state), restored);
  }
  const state = selection(), before = snapshot(state);
  assert.equal(L.removeComparison(state, 'missing'), null);
  assert.equal(L.undoComparison(state, null), false);
  assert.equal(snapshot(state), before);
});

test('R2 undo refuses a filled group without data loss and succeeds when a slot becomes available', () => {
  const state = selection();
  const removed = L.removeComparison(state, 'u02');
  assert.equal(L.addComparison(state, seventh.id, '', catalog), 'ok');
  const full = snapshot(state);
  assert.equal(L.undoComparison(state, removed), false);
  assert.equal(snapshot(state), full);
  assert.equal(state.compareByGroup.ups.includes(seventh.id), true);
  L.removeComparison(state, 'u05');
  assert.equal(L.undoComparison(state, removed), true);
  assert.equal(state.compareByGroup.ups.length, 6);
  assert.equal(new Set(state.compareByGroup.ups).size, 6);
  assert.equal(state.compareByGroup.ups[1], 'u02');
  assert.deepEqual(state.view.pairs.ups, ['u02', 'u04']);
  assert.equal(state.compareByGroup.ups.includes(seventh.id), true);
  assert.deepEqual(state.compareByGroup.optics, ['o01', 'o03']);
});

test('R2 adding and reordering retain the reading pair, differences and stable purchase ID', () => {
  const state = selection(['u02', 'u04']);
  for (const id of ['u01', 'u03', 'u05', 'u06']) {
    assert.equal(L.addComparison(state, id), 'ok');
    assert.deepEqual(state.view.pairs.ups, ['u02', 'u04']);
  }
  for (const [id, delta] of [['u02', 1], ['u03', -1], ['u06', -1]]) {
    assert.equal(L.moveComparison(state, 'ups', id, delta), true);
    assert.deepEqual(state.view.pairs.ups, ['u02', 'u04']);
  }
  assert.deepEqual(L.comparisonKeys(state.view.pairs.ups.map(byId), true), ['Запас енергії', 'Маса']);
  assert.deepEqual(state.view.pairs.optics, ['o03', 'o01']);
  state.cart = {};
  for (let i = 0; i < 3; i++) assert.equal(L.addCartItem(state, 'u02'), 'ok');
  assert.deepEqual(state.cart, {u02: 3});
  assert.equal(L.cartTotal(state.cart), 657000);
  assert.equal(L.addCartItem(state, 'u03'), 'unavailable');
  assert.deepEqual(state.cart, {u02: 3});
});

test('R2 v2 migration retains the accepted R1 selection and initializes research geometry without inventing a position', () => {
  const legacy = {
    version: 2, cart: {u02: 3}, favorites: ['u04'],
    compareByGroup: {ups, optics: ['o01', 'o03']},
    view: {group: 'ups', differences: true, pairs: {ups: ['u02', 'u04'], optics: ['o03', 'o01']},
      pages: {'#/asp/compare': {scroll: 280, details: [], focus: '#differences'}}}
  };
  const state = L.migrateState(legacy);
  assert.equal(state.version, 4);
  assert.deepEqual(state.compareByGroup.ups, ups);
  assert.deepEqual(state.view.pairs.ups, ['u02', 'u04']);
  assert.deepEqual(state.view.pairs.optics, ['o03', 'o01']);
  assert.equal(state.view.differences, true);
  assert.deepEqual(state.cart, {u02: 3});
  assert.equal(state.view.expanded, false);
  assert.equal(state.view.compareBrand, 'asp');
  for (const group of Object.keys(groups)) assert.deepEqual(state.view.research[group], {scroll: 0, x: 0, row: '', offset: 0});
  assert.equal(state.view.pages['#/asp/compare'].scroll, 280);
});

test('R2 research context round-trips by group, bounds geometry, and rejects inherited group keys', () => {
  const state = selection();
  state.view.expanded = true;
  state.view.compareBrand = 'ng';
  state.view.research.ups = {scroll: 812.5, x: 230, row: 'Запас енергії', offset: -16.25};
  state.view.research.optics = {scroll: 130, x: 0, row: 'Моніторинг', offset: 21};
  assert.deepEqual(L.migrateState(JSON.parse(JSON.stringify(state))), state);
  const hostile = JSON.parse('{"view":{"group":"__proto__","expanded":"true","compareBrand":"constructor","research":{"__proto__":{"scroll":99},"ups":{"scroll":-4,"x":"abc","row":9,"offset":999999},"optics":{"scroll":"9999999","x":999999,"row":"Моніторинг","offset":-999999}}}}');
  const normalized = L.migrateState(hostile);
  assert.equal(normalized.view.group, 'ups');
  assert.equal(normalized.view.expanded, false);
  assert.equal(normalized.view.compareBrand, 'asp');
  assert.deepEqual(Object.keys(normalized.view.research), Object.keys(groups));
  assert.deepEqual(normalized.view.research.ups, {scroll: 0, x: 0, row: '', offset: 1000});
  assert.deepEqual(normalized.view.research.optics, {scroll: 100000, x: 10000, row: 'Моніторинг', offset: -1000});
  for (const bad of [null, [], 3, 'bad', {ups: []}]) assert.doesNotThrow(() => L.migrateState({view: {research: bad}}));
});

test('R2 corrupt and denied storage do not masquerade as successfully restored comparison state', () => {
  const corrupt = L.readState({getItem: () => '{"view":'});
  assert.equal(corrupt.status, 'corrupt');
  assert.equal(corrupt.state.recovery.rawState, '{"view":');
  assert.deepEqual({...corrupt.state,recovery:null}, L.initialState());
  const denied = L.readState({getItem: () => { throw new Error('storage unavailable'); }});
  assert.equal(denied.status, 'denied');
  assert.deepEqual(denied.state, L.initialState());
  const normal = selection();
  normal.view.expanded = true;
  normal.view.research.ups = {scroll: 460, x: 0, row: 'Маса', offset: 12};
  let stored;
  const memory = {getItem: () => stored, setItem: (key, value) => {assert.equal(key, L.STATE_KEY); stored = value;}};
  assert.equal(L.writeState(memory, normal), true);
  assert.equal(L.readState(memory).status, 'ok');
  assert.deepEqual(L.readState(memory).state, normal);
});
