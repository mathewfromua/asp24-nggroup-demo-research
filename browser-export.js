// Browser capabilities are optional. A dispatched click does not prove that a
// WebView saved a file, so every export also exposes its exact text on this page.
export function requestTextDownload(text, name, env=globalThis) {
  let link, url;
  try {
    const {document, URL, Blob}=env;
    if(!document?.body||typeof Blob!=='function'||typeof URL?.createObjectURL!=='function')return false;
    link=document.createElement('a');
    if(!('download' in link))return false;
    const json=name.toLowerCase().endsWith('.json');
    url=URL.createObjectURL(new Blob([json?text:'\ufeff'+text],{type:json?'application/json':'text/plain;charset=utf-8'}));
    link.href=url;link.download=name;link.hidden=true;document.body.append(link);
    link.click();
    return true; // Requested, never confirmation that a file was saved.
  } catch { return false; }
  finally {
    link?.remove();
    if(url)env.setTimeout(()=>{try{env.URL.revokeObjectURL?.(url);}catch{}},60000);
  }
}

export async function copyText(text, env=globalThis) {
  try {
    if(typeof env.navigator?.clipboard?.writeText!=='function')return false;
    await env.navigator.clipboard.writeText(text);
    return true;
  } catch { return false; }
}

/** Always present, including when an in-app browser silently ignores download. */
export function presentTextExport(container, text, name, {download=true, env=globalThis}={}) {
  const doc=container.ownerDocument;
  container.querySelector('.export-fallback')?.remove();
  const panel=doc.createElement('section');panel.className='export-fallback';panel.setAttribute('aria-label','Копія для збереження');
  const status=doc.createElement('p');status.className='status-save';status.setAttribute('role','status');
  const details=doc.createElement('details');
  const summary=doc.createElement('summary');summary.textContent='Скопіювати текст замість завантаження';
  const label=doc.createElement('label');label.className='field';label.textContent=name;label.style.overflowWrap='anywhere';
  const area=doc.createElement('textarea');area.readOnly=true;area.rows=10;area.value=text;area.spellcheck=false;
  area.setAttribute('aria-label','Повний текст копії '+name);area.style.fontSize='16px';
  label.append(area);
  const actions=doc.createElement('div');actions.className='modal-actions';
  const select=doc.createElement('button');select.type='button';select.className='btn secondary';select.textContent='Виділити весь текст';
  const copy=doc.createElement('button');copy.type='button';copy.className='btn secondary';copy.textContent='Копіювати текст';
  const selectText=()=>{details.open=true;area.focus();area.select();area.setSelectionRange(0,area.value.length);};
  select.addEventListener('click',selectText);
  copy.addEventListener('click',async()=>{
    const copied=await copyText(text,env);
    if(!panel.isConnected)return;
    status.textContent=copied?'Текст скопійовано.':'Автокопіювання недоступне. Текст виділено: скористайтеся командою копіювання браузера.';
    if(!copied)selectText();
  });
  actions.append(copy,select);details.append(summary,label,actions);panel.append(status,details);container.append(panel);
  const requested=download&&requestTextDownload(text,name,env);
  status.textContent=requested?'Файл підготовлено. Перевірте завантаження; якщо файл не з’явився, скопіюйте текст нижче.':download?'Завантаження недоступне. Повний текст залишено тут для копіювання й збереження.':'Автокопіювання недоступне. Повний текст залишено тут: виділіть і скопіюйте його командою браузера.';
  details.open=!requested;
  if(!requested)selectText();
  return {requested,panel};
}
