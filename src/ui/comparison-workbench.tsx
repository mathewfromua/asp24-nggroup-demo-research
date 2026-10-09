import {useEffect, useRef, useState} from 'react';
import {createRoot, type Root} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {money} from '../data/catalog.ts';
import {comparisonRows} from '../domain/comparison.ts';
import {quantityLabel} from '../domain/cart.ts';
import type {Brand, GroupId, Product} from '../domain/types.ts';
import '../styles/comparison-workbench.css';

export interface WorkbenchSnapshot {
  brand: Brand;
  group: GroupId;
  groups: {id: GroupId; name: string; count: number}[];
  candidates: Product[];
  pair: string[];
  differences: boolean;
  undoAvailable: boolean;
  saveLabel: string;
  storageWarning: string;
  catalogHref: string;
  legacyHref: string;
  cart: Record<string, number>;
}
export interface WorkbenchActions {
  search(query: string): Product[];
  add(id: string, replaceId?: string): boolean;
  remove(id: string): void;
  undo(): boolean;
  pair(slot: number, id: string): void;
  group(id: GroupId): void;
  differences(enabled: boolean): void;
  details(id: string): void;
  cart(id: string): boolean;
  shortlist(ids: string[]): void;
  save(): boolean;
}
const price = (p: Product) => money(p.price);
const name = (p: Product) => `${p.name} · ${p.sku}`;

function Workbench({snapshot: s, actions: a}: {snapshot: WorkbenchSnapshot; actions: WorkbenchActions}) {
  const [discovery, setDiscovery] = useState(false);
  const [query, setQuery] = useState('');
  const [replaceId, setReplaceId] = useState('');
  const [message, setMessage] = useState('');
  const searchRef = useRef<HTMLInputElement>(null);
  const addRef = useRef<HTMLButtonElement>(null);
  const candidateDetails = useRef<HTMLDetailsElement>(null);
  const mobile = useRef(matchMedia('(max-width: 700px)').matches);
  const pair = s.pair.map(id => s.candidates.find(p => p.id === id)).filter((p): p is Product => !!p);
  const results = discovery ? a.search(query) : [];
  const activeGroup = s.groups.find(g => g.id === s.group)?.name || s.group;
  useEffect(() => {const media=matchMedia('(max-width: 700px)');const changed=()=>{mobile.current=media.matches;if(candidateDetails.current)candidateDetails.current.open=!media.matches;};media.addEventListener('change',changed);return ()=>media.removeEventListener('change',changed);}, []);
  useEffect(() => {if (discovery) searchRef.current?.focus();}, [discovery, replaceId]);
  useEffect(() => {setQuery('');setReplaceId('');setDiscovery(false);}, [s.group]);
  function openDiscovery(id = '') {setReplaceId(id);setDiscovery(true);}
  function closeDiscovery() {setDiscovery(false);setReplaceId('');addRef.current?.focus();}
  function add(p: Product) {
    const replaced = s.candidates.find(candidate => candidate.id === replaceId);
    if (a.add(p.id, replaceId)) {
      setMessage(replaced ? `${replaced.name} замінено на ${p.name}.` : `${p.name}: додано до порівняння.`);
      setReplaceId('');
      searchRef.current?.focus();
    } else setMessage('Добір не змінено. Перевірте ліміт і вибір моделі для заміни.');
  }
  function remove(p: Product) {a.remove(p.id);setMessage(`${p.name}: прибрано. Дію можна скасувати.`);requestAnimationFrame(() => document.querySelector<HTMLButtonElement>('[data-testid="wb-undo"]')?.focus());}
  function undo() {setMessage(a.undo() ? 'Видаленого кандидата повернуто.' : 'Немає місця для повернення. Поточний добір не змінено.');}
  function cart(p: Product) {setMessage(a.cart(p.id) ? `${p.name}: додано ${quantityLabel(p,1)} до поточного кошика.` : 'Кошик не змінено. Перевірте наявність і кількість.');}
  function saveSelection() {
    const persisted = a.save();
    setMessage('');
    requestAnimationFrame(() => setMessage(persisted ? 'Вибір збережено. Він доступний після перезавантаження.' : 'Вибір лише в пам’яті цієї сторінки. Перезавантаження може його втратити; збережіть JSON-експорт.'));
  }
  function table(models: Product[], variant: 'full'|'pair') {
    const rows = comparisonRows(models, s.differences && models.length > 1);
    return <div className={`wb-table-wrap wb-${variant}`} tabIndex={0} aria-label={`Параметри: ${variant === 'pair' ? 'активна пара' : 'усі кандидати'}`}>
      <table className="wb-table">
        <caption className="sr-only">{activeGroup}. {variant === 'pair' ? 'Активна пара' : 'Усі кандидати'}. {s.differences ? 'Відмінності та неповні дані' : 'Усі параметри'}</caption>
        <thead><tr><th scope="col" className="wb-parameter-heading">Параметр<span>Значення для конкретного виконання</span></th>{models.map(p => <th scope="col" key={p.id} data-pair={s.pair[0] === p.id ? 'A' : s.pair[1] === p.id ? 'B' : undefined}>
          <button type="button" className="wb-model-title" onClick={() => a.details(p.id)} aria-label={`Докладніше: ${p.name}`}>{p.name}</button>
          <span className="wb-sku">{p.sku} · {p.revision}</span>
          <span className="wb-pair-marker">{s.pair[0] === p.id ? 'A · активна пара' : s.pair[1] === p.id ? 'B · активна пара' : 'Кандидат'}</span>
        </th>)}</tr></thead>
        <tbody>
          <tr className="wb-offers"><th scope="row">Умовна ціна / наявність</th>{models.map(p => <td key={p.id}><strong>{price(p)}</strong><span>за {p.unit}</span><span className={p.available ? 'wb-stock' : 'wb-stock unavailable'}>{p.available ? 'В наявності' : 'Немає в наявності'}</span></td>)}</tr>
          {rows.map(row => <tr key={row.key} data-row={row.key} className={row.different ? 'wb-different' : row.incomplete ? 'wb-incomplete' : ''}>
            <th scope="row">{row.label}{row.different && <span className="wb-row-note">Відмінність</span>}{row.incomplete && <span className="wb-row-note">Неповні дані</span>}</th>
            {row.cells.map(cell => <td key={cell.productId} data-product-id={cell.productId} className={`wb-value-${cell.value.status}`}>{cell.text}</td>)}
          </tr>)}
          {!rows.length && <tr><td colSpan={models.length + 1}>Відомих відмінностей і прогалин у технічних параметрах немає.</td></tr>}
        </tbody>
        <tfoot><tr><th scope="row">Короткий список</th>{models.map(p => <td key={p.id}><button type="button" className="wb-secondary" onClick={() => a.shortlist([p.id])} aria-label={`У проєкт: ${p.name}`}>У проєкт</button><button type="button" className="wb-text" disabled={!p.available} onClick={() => cart(p)} aria-label={`До кошика: ${p.name}`}>До кошика{s.cart[p.id] ? ` · ${s.cart[p.id]} ${p.unit}` : ''}</button></td>)}</tr></tfoot>
      </table>
    </div>;
  }
  return <section className="comparison-workbench" data-testid="comparison-workbench" data-group={s.group} aria-labelledby="wb-title">
    <div className="wb-heading"><div><a href={s.catalogHref} className="wb-back">← До добору</a><h1 id="wb-title">Робочий простір порівняння</h1></div><div className="wb-heading-side"><span className="wb-count">{s.candidates.length}<small> / 6 кандидатів</small></span><a href={s.legacyHref}>Класичне порівняння</a></div></div>
    <div className="wb-toolbar"><label className="wb-field">Категорія<select data-testid="wb-group" id="wb-group" value={s.group} onChange={event => a.group(event.target.value as GroupId)}>{s.groups.map(group => <option key={group.id} value={group.id}>{group.name} · {group.count}</option>)}</select></label><button type="button" className="wb-primary" data-testid="wb-add" ref={addRef} aria-expanded={discovery} aria-controls="wb-discovery" onClick={() => discovery ? closeDiscovery() : openDiscovery()}>＋ Додати / замінити</button><button type="button" className="wb-secondary" data-testid="wb-shortlist" disabled={!s.candidates.length} onClick={() => a.shortlist(s.candidates.map(p => p.id))}>Зберегти в проєкті</button></div>
    {discovery && <section id="wb-discovery" className="wb-discovery" aria-label="Додавання та заміна кандидатів"><div className="wb-discovery-heading"><h2>{replaceId ? 'Замінити кандидата' : 'Додати до порівняння'}</h2><button type="button" className="wb-secondary" onClick={closeDiscovery}>Готово</button></div>
      <div className="wb-discovery-controls"><label className="wb-field">Пошук у категорії<input type="search" ref={searchRef} data-testid="wb-search" id="wb-search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Модель, артикул або виробник" autoComplete="off"/></label><label className="wb-field">Дія<select value={replaceId} data-testid="wb-replace-target" onChange={event => setReplaceId(event.target.value)}><option value="">Додати нового кандидата</option>{s.candidates.map(p => <option key={p.id} value={p.id}>Замість {name(p)}</option>)}</select></label></div>
      {s.candidates.length >= 6 && !replaceId && <p className="wb-notice">У доборі вже шість моделей. Оберіть, кого замінити: решта кандидатів збережеться.</p>}
      <p className="wb-result-count" role="status">{results.length} моделей за запитом · категорія {activeGroup}</p>
      <div className="wb-results">{results.map(p => {const selected = s.candidates.some(item => item.id === p.id);return <article key={p.id} data-testid={`wb-result-${p.id}`} data-selected={selected}><div><h3>{p.name}</h3><p className="wb-sku">{p.sku} · виконання {p.revision}</p><p>{p.available ? 'В наявності' : 'Немає в наявності'} · {price(p)} / {p.unit}</p></div><button type="button" className="wb-secondary" data-testid={`wb-add-${p.id}`} disabled={selected || s.candidates.length >= 6 && !replaceId} onClick={() => add(p)}>{selected ? 'Додано' : replaceId ? 'Замінити' : 'Додати'}</button></article>;})}{!results.length && <p>Моделей не знайдено. Уточніть назву або артикул.</p>}</div>
    </section>}
    {!!s.candidates.length && <>
      <div className="wb-pair-controls" role="group" aria-label="Активна пара"><span>Активна пара</span>{[0,1].map(slot => <label key={slot} className="wb-pair-select"><span aria-hidden="true">{slot === 0 ? 'A' : 'B'}</span><span className="sr-only">Модель {slot === 0 ? 'A' : 'B'}</span><select data-testid={slot === 0 ? 'wb-pair-a' : 'wb-pair-b'} value={s.pair[slot] || ''} onChange={event => {a.pair(slot,event.target.value);setMessage(`Модель ${slot === 0 ? 'A' : 'B'}: ${s.candidates.find(p => p.id === event.target.value)?.name || 'не вибрано'}.`);}}>{!s.pair[slot] && <option value="">Додайте другу модель</option>}{s.candidates.map(p => <option key={p.id} value={p.id}>{name(p)}</option>)}</select></label>)}</div>
      <details className="wb-candidates" ref={candidateDetails} open={!mobile.current}><summary>Керувати кандидатами · {s.candidates.length} із 6</summary><div className="wb-candidate-grid">{s.candidates.map(p => <article key={p.id} data-testid={`wb-candidate-${p.id}`} data-pair={s.pair[0] === p.id ? 'A' : s.pair[1] === p.id ? 'B' : undefined}><strong>{p.name}</strong><span className="wb-sku">{p.sku}</span>{s.pair.includes(p.id) && <span className="wb-candidate-pair">{s.pair[0] === p.id ? 'A' : 'B'} · активна пара</span>}<div><button type="button" className="wb-text" data-testid={`wb-replace-${p.id}`} onClick={() => openDiscovery(p.id)}>Замінити</button><button type="button" className="wb-text" data-testid={`wb-remove-${p.id}`} aria-label={`Прибрати ${p.name}`} onClick={() => remove(p)}>Прибрати</button></div></article>)}</div></details>
      <div className="wb-modes"><label><input type="checkbox" data-testid="wb-differences" checked={s.differences} onChange={event => a.differences(event.target.checked)}/> Лише відмінності</label><span>{s.differences ? 'Відмінності та неповні дані' : 'Усі параметри'}</span><button type="button" className="wb-text" data-testid="wb-undo" disabled={!s.undoAvailable} onClick={undo}>↶ Скасувати видалення</button></div>
      {table(s.candidates,'full')}{table(pair,'pair')}
    </>}
    {!s.candidates.length && <div className="wb-empty"><span aria-hidden="true">A ↔ B</span><h2>Знайдіть обладнання для свого завдання</h2><p>Додайте до шести моделей однієї категорії. Виберіть активну пару, зіставте параметри та збережіть потрібні позиції в проєкті.</p><button type="button" className="wb-primary" onClick={() => openDiscovery()}>Обрати першу модель</button>{s.undoAvailable && <button type="button" className="wb-secondary" data-testid="wb-undo" onClick={undo}>Скасувати видалення</button>}</div>}
    <div className="wb-footer"><p>Невідоме значення не дорівнює нулю. «Не уточнено» / «Параметр відсутній» / «Не застосовується» позначено окремо; суперечності не приховано.</p><div><button type="button" className="wb-secondary" data-testid="wb-save" onClick={saveSelection}>Зберегти вибір</button><span data-save-status data-testid="wb-save-status" role="status" aria-live="polite">{s.saveLabel}</span></div></div>
    <p className="wb-action-status" role="status" aria-live="polite">{message}</p>
  </section>;
}
export function mountWorkbench(element: HTMLElement, snapshot: WorkbenchSnapshot, actions: WorkbenchActions): {update(snapshot: WorkbenchSnapshot): void; destroy(): void} {
  const root: Root = createRoot(element);
  const update = (next: WorkbenchSnapshot) => flushSync(() => root.render(<Workbench snapshot={next} actions={actions}/>));
  update(snapshot);
  return {update, destroy: () => root.unmount()};
}
