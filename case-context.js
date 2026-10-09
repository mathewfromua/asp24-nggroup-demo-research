// Isolated, versioned examples. The backing store never receives the personal STATE_KEY.
import {initialState, STATE_KEY} from './logic.js';
import {byId, groups} from './data.js';
import {inspectOrders} from './orders.js';
import {validateProject} from './science.js';
import {assetUrl} from './asset-url.js';
export const caseContext={active:false,storage:null,record:null,getState:null};
export function seedCase(record) {
  const state=initialState(),seed=record.seed;
  if(seed.group){state.view.group=seed.group;state.compareByGroup[seed.group]=[...seed.candidates];state.view.pairs[seed.group]=[...seed.pair];state.view.differences=seed.differences===true;}
  if(seed.cart)state.cart={...seed.cart};
  if(seed.drafts)state.drafts=structuredClone(seed.drafts);
  return state;
}
export function isolatedStorage(backing,key,seed) {
  if(!/^asp24-nggroup-case:[a-z0-9-]+:v[1-9]\d*$/.test(key))throw new Error('Unexpected case storage key');
  let memory=JSON.stringify(seed),discardWrites=false,readFailed=false;
  let status={kind:'memory-only',persisted:false};
  const listeners=new Set();
  const update=kind=>{status=Object.freeze({kind,persisted:kind==='persisted'});for(const listener of listeners)listener(status);return status;};
  const unavailable=()=>!backing||typeof backing.getItem!=='function'||typeof backing.setItem!=='function';
  function persist(value){
    if(unavailable()){update('memory-only');throw new Error('Case session storage unavailable');}
    // An unreadable old value must not be overwritten by an automatic save.
    if(readFailed){update('read-error');throw new Error('Case session storage could not be read');}
    try{backing.setItem(key,value);}catch(error){update('write-error');throw error;}
    update('persisted');
  }
  if(!unavailable()){
    try{
      const saved=backing.getItem(key);
      if(saved!==null){
        const parsed=JSON.parse(saved);
        if(parsed?.version!==4)throw new Error('Unsupported case state schema');
        memory=saved;update('persisted');
      }else persist(memory);
    }catch(error){
      // A write failure during initial seeding already has its distinct status.
      if(status.kind!=='write-error'){readFailed=true;update('read-error');}
    }
  }
  return {
    get status(){return status;},
    subscribe(listener){listeners.add(listener);listener(status);return ()=>listeners.delete(listener);},
    getItem(name){if(name!==STATE_KEY)return null;return memory;},
    setItem(name,value){
      if(name!==STATE_KEY)throw new Error('Unexpected storage key');
      // A successful reset is followed by navigation: reject stale pagehide saves.
      if(discardWrites)throw new Error('Case reset is awaiting reload');
      memory=value;
      persist(value);
    },
    // Roll back an uncommitted transaction in memory; never retry a failed write.
    retainState(state){memory=JSON.stringify(state);},
    reset(){
      try{
        if(!backing||typeof backing.removeItem!=='function')throw new Error('Case session storage unavailable');
        backing.removeItem(key);
      }catch{update('clear-error');return {ok:false,status};}
      discardWrites=true;memory=JSON.stringify(seed);readFailed=false;
      return {ok:true,status:update('persisted')};
    }
  };
}
export function caseStorageMessage(status) {
  if(status.kind==='persisted')return 'Стан прикладу збережено в цій вкладці й буде відновлено після перезавантаження.';
  const reason={
    'memory-only':'Сховище вкладки недоступне.',
    'read-error':'Не вдалося прочитати попередній стан прикладу. Запис у сховище призупинено, щоб не перезаписати непрочитані дані.',
    'write-error':'Не вдалося записати зміни прикладу у сховище.',
    'clear-error':'Не вдалося очистити сховище. Приклад не скинуто й сторінку не перезавантажено.'
  }[status.kind]||'Збереження не підтверджено.';
  return reason+' Поточні дані є лише в пам’яті цієї вкладки; перезавантаження або закриття може їх втратити. Збережіть їх кнопкою «Експортувати стан прикладу (JSON)».';
}
export function caseSaveLabel(status) {
  return status.persisted?'Збережено у сховищі цієї вкладки.':'Лише в пам’яті цієї вкладки. Перезавантаження може втратити зміни; експортуйте JSON.';
}
const isRecord=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
export function validateCaseExport(payload,record) {
  if(!isRecord(payload)||payload.format!=='asp24-nggroup-case-state'||payload.exportVersion!==1||payload.stateSchemaVersion!==4)return 'Невідомий формат або версія експорту прикладу.';
  if(typeof payload.caseId!=='string'||!/^[a-z0-9-]+$/.test(payload.caseId)||!Number.isInteger(payload.caseVersion)||payload.caseVersion<1)return 'Некоректна ідентичність прикладу.';
  if(record&&(payload.caseId!==record.caseId||payload.caseVersion!==record.caseVersion))return 'Експорт належить іншому прикладу.';
  const s=payload.state;
  if(!isRecord(s)||s.version!==4||!isRecord(s.cart)||!isRecord(s.drafts)||!isRecord(s.science)||!isRecord(s.compareByGroup)||!isRecord(s.view)||!isRecord(s.view.pairs)||!Array.isArray(s.orders)||!Array.isArray(s.favorites)||typeof s.note!=='string'||typeof s.listName!=='string'||!isRecord(s.checkout)||!isRecord(s.catalogs))return 'Пошкоджена структура стану прикладу.';
  if(Object.entries(s.cart).some(([id,q])=>!byId(id)||!Number.isInteger(q)||q<1||q>999)||s.favorites.some(id=>!byId(id)))return 'Невідома модель або некоректна кількість.';
  for(const group of Object.keys(groups)){
    const ids=s.compareByGroup[group],pair=s.view.pairs[group];
    if(!Array.isArray(ids)||ids.length>6||new Set(ids).size!==ids.length||ids.some(id=>byId(id)?.group!==group)||!Array.isArray(pair)||pair.length>2||new Set(pair).size!==pair.length||pair.some(id=>!ids.includes(id)))return 'Некоректний добір або активна пара.';
  }
  if(Object.entries(s.drafts).some(([id,d])=>!byId(id)?.ng||!isRecord(d)||!['Сумісність','Партія','Тест'].includes(d.purpose)||typeof d.quantity!=='string'||typeof d.question!=='string'||d.question.length>1500))return 'Пошкоджена чернетка прикладу.';
  if(inspectOrders(s.orders).quarantined.length)return 'Пошкоджена історія демозамовлень.';
  if(Object.keys(s.science).length&&(s.science.version!==1||!Array.isArray(s.science.projects)||s.science.projects.length>30||s.science.projects.some(p=>validateProject(p))))return 'Пошкоджені навчальні проєкти.';
  return null;
}
export function createCaseExport(record,state) {
  // Preserve entered text verbatim. Validation must never silently normalize it.
  const payload=JSON.parse(JSON.stringify({format:'asp24-nggroup-case-state',exportVersion:1,caseId:record.caseId,caseVersion:record.caseVersion,stateSchemaVersion:4,state}));
  const error=validateCaseExport(payload,record);if(error)throw new Error(error);
  return JSON.stringify(payload,null,2);
}
export async function prepareCase() {
  const query=new URLSearchParams(location.search);
  if(!query.has('case'))return true;
  caseContext.active=true;
  const registry=await fetch(assetUrl('publication.json')).then(r=>{if(!r.ok)throw new Error('Registry unavailable');return r.json();});
  const id=query.get('case'),version=query.get('v')||'1';
  const known=registry.cases.find(c=>c.caseId===id);
  const record=registry.cases.find(c=>c.caseId===id&&String(c.caseVersion)===version);
  const banner=document.createElement('aside');banner.className='case-banner';banner.setAttribute('aria-label','Дослідницький приклад');
  function text(tag,value){const el=document.createElement(tag);el.textContent=value;banner.append(el);return el;}
  if(!record){
    text('h1','Ця версія прикладу недоступна');text('p',known?.purpose||'Запит не відповідає жодному з чотирьох опублікованих прикладів. Особисті дані не змінено.');
    const a=text('a','Повернутися до огляду');a.href=known?assetUrl(`reports/${known.reportId}_Review.html`)+`#${known.sectionId}`:assetUrl('index.html');
    document.body.prepend(banner);return false;
  }
  caseContext.record=record;
  let backing;try{backing=window.sessionStorage;}catch{}
  caseContext.storage=isolatedStorage(backing,`asp24-nggroup-case:${record.caseId}:v${record.caseVersion}`,seedCase(record));
  const disclosure=text('details','');disclosure.className='case-context-details';
  const summary=document.createElement('summary');summary.textContent=record.title+' · v'+record.caseVersion+' · контекст і дії';disclosure.append(summary);
  const purpose=text('p',record.purpose);disclosure.append(purpose);
  const isolation=text('small','Окремий навчальний стан цієї вкладки. Ваші кошик, проєкти й чернетки не змінюються.');disclosure.append(isolation);
  text('p','Навчальний приклад · товари й ціни умовні.').className='case-demo-notice';
  const status=text('p','');status.id='case-storage-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');status.setAttribute('aria-atomic','true');
  caseContext.storage.subscribe(value=>{status.dataset.storageKind=value.kind;const message=value.persisted?caseSaveLabel(value):caseStorageMessage(value);if(status.textContent!==message)status.textContent=message;});
  const nav=text('nav','');nav.setAttribute('aria-label','Дії та повернення з прикладу');
  disclosure.append(nav);
  const a=text('a','Повернутися до розділу огляду');a.href=assetUrl(`reports/${record.reportId}_Review.html`)+`#${record.sectionId}`;
  const exportButton=document.createElement('button');exportButton.id='case-export';exportButton.textContent='Експортувати стан прикладу (JSON)';
  const exportStatus=text('p','');exportStatus.id='case-export-status';exportStatus.setAttribute('role','status');
  exportButton.addEventListener('click',()=>{
    try{
      const state=caseContext.getState?.()||JSON.parse(caseContext.storage.getItem(STATE_KEY));
      const json=createCaseExport(record,state),url=URL.createObjectURL(new Blob([json],{type:'application/json'})),link=document.createElement('a');
      link.href=url;link.download=`ASP24-NGGroup-case-${record.caseId}-v${record.caseVersion}.json`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1500);
      exportStatus.textContent='JSON поточного навчального стану підготовлено для завантаження. Перевірте файл у завантаженнях; особисті проєкти не включено.';
    }catch(error){exportStatus.textContent='Експорт не створено: '+error.message;}
  });nav.append(exportButton);
  const resetStatus=text('p','');resetStatus.id='case-reset-status';resetStatus.setAttribute('role','status');
  const reset=document.createElement('button');reset.id='case-reset';reset.textContent='Почати приклад спочатку';reset.addEventListener('click',()=>{if(!caseContext.storage.reset().ok){resetStatus.textContent='Приклад не скинуто: очищення сховища не вдалося. Поточні зміни залишено; можна експортувати JSON.';return;}const modern=new URLSearchParams(location.hash.split('?')[1]||'').get('experience')==='modern';location.hash=record.route+(modern&&record.route.endsWith('/compare')?'?experience=modern':'');location.reload();});nav.append(reset);
  document.body.prepend(banner);
  if(!location.hash)history.replaceState(null,'',location.pathname+location.search+record.route);
  const syncDisclosure=()=>{disclosure.open=!/\/compare\?/.test(location.hash)||new URLSearchParams(location.hash.split('?')[1]||'').get('experience')!=='modern';};
  syncDisclosure();window.addEventListener('hashchange',syncDisclosure);
  return true;
}
