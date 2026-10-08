import test from 'node:test';
import assert from 'node:assert/strict';
import { numericValue } from '../data.js';
import { initialState, filterProducts } from '../logic.js';
import { renderCatalog } from '../catalog-ui.js';
import { normalizeScience, createProject, handleScience, renderScience } from '../science.js';

// These tests use production modules and rendered HTML, not extracted app.js source.
// They do not substitute for the two real DOM acceptance checks below.
const decode = text => text.replace(/&(amp|lt|gt|quot|#39);/g, (_, entity) =>
  ({ amp: '&', lt: '<', gt: '>', quot: '"', '#39': "'" })[entity]);
function buttons(html, action) {
  return [...html.matchAll(/<button\b([^>]*)>/g)].map(([, attributes]) => {
    const dataset = Object.fromEntries([...attributes.matchAll(/data-([\w-]+)="([^"]*)"/g)]
      .map(([, key, value]) => [key, decode(value)]));
    return { dataset, disabled: /(?:^|\s)disabled(?:\s|$)/.test(attributes) };
  }).filter(button => button.dataset.action === action);
}
function scienceFixture() {
  const state = initialState();
  state.science = normalizeScience();
  const calls = { modals: [], messages: [], renders: 0 };
  const helpers = {
    save: () => true,
    render: () => { calls.renders++; },
    toast: message => calls.messages.push(message),
    openModal: html => calls.modals.push(html),
    closeModal: () => {},
    go: () => {},
    downloadText: () => {}
  };
  return { state, calls, helpers };
}

test('F-01: each OR chip identifies its own value; remaining 36 W condition selects exact models', () => {
  const params = new URLSearchParams('cat=ups&q=VOLTYN&f0=18+Вт&f0=36+Вт&available=1&sort=price-down&view=list');
  const html = renderCatalog({
    route: { brand: 'asp', params }, state: initialState(),
    productCard: () => '', compareButton: () => '', favoriteButton: () => '',
    cartButton: () => '', icon: () => '', empty: () => '', dock: () => ''
  });
  const chips = buttons(html, 'remove-filter').map(button => button.dataset);
  assert.deepEqual(chips.filter(chip => chip.key === 'f0').map(chip => chip.value), ['18 Вт', '36 Вт']);
  assert.equal(chips.find(chip => chip.key === 'q').value, 'VOLTYN');
  assert.equal(chips.find(chip => chip.key === 'available').value, '1');

  // Expected resulting URL; the actual app click requires the skipped DOM check.
  const remaining = new URLSearchParams('cat=ups&q=VOLTYN&f0=36+Вт&available=1&sort=price-down&view=list');
  assert.deepEqual(filterProducts('asp', remaining).map(product => product.id), ['u04', 'u02']);
});

test('F-02: explicit price and numeric order remain primary over an exact model match', () => {
  const expected = new Map([
    ['', ['u02', 'u04']],
    ['price-up', ['u02', 'u04']],
    ['price-down', ['u04', 'u02']],
    ['energyWh-up', ['u02', 'u04']],
    ['energyWh-down', ['u04', 'u02']]
  ]);
  for (const [sort, ids] of expected) {
    const actual = filterProducts('asp', new URLSearchParams({ cat: 'ups', q: 'VOLTYN N36', sort }));
    assert.deepEqual(actual.map(product => product.id), ids, sort || 'default relevance');
  }
  for (const sort of ['massG-up', 'massG-down']) {
    const actual = filterProducts('asp', new URLSearchParams({ cat: 'ups', q: 'VOLTYN', sort }));
    const values = actual.map(product => numericValue(product, 'massG'));
    const firstUnknown = values.indexOf(null);
    assert.ok(firstUnknown > 0, `${sort}: fixture contains known and unknown masses`);
    assert.ok(values.slice(firstUnknown).every(value => value === null), `${sort}: unknown remains last`);
    const known = values.slice(0, firstUnknown);
    assert.ok(known.every((value, index) => !index ||
      (sort.endsWith('-up') ? value >= known[index - 1] : value <= known[index - 1])));
  }
});

test('F-03: serial candidate additions preserve rendered query/group and do not mix working selections', () => {
  const { state, calls, helpers } = scienceFixture();
  state.cart = { c04: 2 };
  state.compareByGroup.ups = ['u08'];
  const project = createProject(state.science, { name: 'Резерв для мережі' });
  const other = createProject(state.science, { name: 'Інший об’єкт', candidates: ['c02'] });
  handleScience('science-submit', {
    form: 'candidate-search', project: project.id, values: { q: 'VOLTYN', group: 'ups' }
  }, state, helpers);
  const initialButtons = buttons(calls.modals.at(-1), 'science-add-candidate');
  const expectedIds = initialButtons.map(button => button.dataset.id);
  assert.equal(expectedIds.length, 8);

  for (const id of ['u02', 'u04']) {
    const action = buttons(calls.modals.at(-1), 'science-add-candidate')
      .find(button => button.dataset.id === id);
    assert.equal(action.dataset.query, 'VOLTYN');
    assert.equal(action.dataset.group, 'ups');
    handleScience('science-add-candidate', action.dataset, state, helpers);
    const html = calls.modals.at(-1);
    assert.match(html, /name="q" value="VOLTYN"/);
    assert.match(html, /value="ups" selected/);
    const result = buttons(html, 'science-add-candidate');
    assert.deepEqual(result.map(button => button.dataset.id), expectedIds);
    assert.equal(result.find(button => button.dataset.id === id).disabled, true);
  }
  assert.deepEqual(project.candidates, ['u02', 'u04']);
  assert.deepEqual(project.quantities, { u02: 1, u04: 1 });
  assert.deepEqual(project.chosen, []);
  assert.deepEqual(other.candidates, ['c02']);
  assert.deepEqual(state.cart, { c04: 2 });
  assert.deepEqual(state.compareByGroup.ups, ['u08']);
});

test('F-05 persistence boundary: explicit metadata save survives auxiliary changes and state restoration', () => {
  const { state, calls, helpers } = scienceFixture();
  const project = createProject(state.science, { name: 'Початкова назва', candidates: ['u02'] });
  const values = { name: 'Резерв для кабінету', note: 'Звірити напругу, полярність і роз’єм.\nПотрібно 2 одиниці.' };
  handleScience('science-submit', { form: 'project', project: project.id, values }, state, helpers);
  handleScience('science-field', { project: project.id, field: 'quantity', id: 'u02', value: '2' }, state, helpers);
  handleScience('science-field', { project: project.id, field: 'chosen', id: 'u02', checked: true }, state, helpers);
  handleScience('science-add-candidate', { project: project.id, id: 'u04', query: 'VOLTYN', group: 'ups' }, state, helpers);
  assert.equal(project.name, values.name);
  assert.equal(project.note, values.note);
  assert.equal(project.quantities.u02, 2);
  assert.deepEqual(project.chosen, ['u02']);

  const restored = normalizeScience(JSON.parse(JSON.stringify(state.science)));
  const recovered = restored.projects.find(item => item.id === project.id);
  assert.equal(recovered.name, values.name);
  assert.equal(recovered.note, values.note);
  const html = renderScience({ page: 'project', id: project.id, params: new URLSearchParams() }, { science: restored }, 'asp');
  assert.ok(html.includes(values.name));
  assert.ok(html.includes(values.note));

  handleScience('science-submit', {
    form: 'project', project: project.id, values: { name: '', note: 'Незавершений запис' }
  }, state, helpers);
  assert.equal(project.name, values.name);
  assert.equal(project.note, values.note);
  assert.ok(calls.messages.some(message => message.includes('Назва має містити')));
});

const browserBlocked = 'Local browser acceptance blocked: localhost EPERM; file URL security block. Public v13 is not this edited release. No alternative browser used for acceptance.';
test('F-01 DOM acceptance: click 18 W chip keeps 36 W plus query/sort/view', { skip: browserBlocked }, () => {});
test('F-05 DOM acceptance: unsaved and temporarily empty metadata survive candidate/quantity/checkbox actions; Save then reload restores committed text', { skip: browserBlocked }, () => {});
