// Isolated, versioned examples. This module never reads the personal STATE_KEY.
import {initialState, STATE_KEY} from './logic.js';
import {assetUrl} from './asset-url.js';
export const caseContext={active:false,storage:null,record:null};
export function seedCase(record) {
  const state=initialState(),seed=record.seed;
  if(seed.group){state.view.group=seed.group;state.compareByGroup[seed.group]=[...seed.candidates];state.view.pairs[seed.group]=[...seed.pair];state.view.differences=seed.differences===true;}
  if(seed.cart)state.cart={...seed.cart};
  if(seed.drafts)state.drafts=structuredClone(seed.drafts);
  return state;
}
export function isolatedStorage(backing,key,seed) {
  let memory=JSON.stringify(seed),discardWrites=false;
  try{const saved=backing?.getItem(key);if(saved&&JSON.parse(saved)?.version===4)memory=saved;}catch{}
  return {
    getItem(name){if(name!==STATE_KEY)return null;return memory;},
    setItem(name,value){if(name!==STATE_KEY)throw new Error('Unexpected storage key');if(discardWrites)return;try{backing?.setItem(key,value);}catch{}memory=value;},
    // Ignore pagehide/hashchange saves from the old app instance until reload.
    reset(){discardWrites=true;memory=JSON.stringify(seed);try{backing?.removeItem(key);}catch{}}
  };
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
  text('strong',record.title+' · приклад v'+record.caseVersion);
  text('p',record.purpose);
  text('small','Окремий навчальний стан цієї вкладки. Ваші кошик, проєкти й чернетки не змінюються.');
  const nav=text('nav','');nav.setAttribute('aria-label','Повернення з прикладу');
  const a=document.createElement('a');a.textContent='Повернутися до розділу огляду';a.href=assetUrl(`reports/${record.reportId}_Review.html`)+`#${record.sectionId}`;nav.append(a);
  const reset=document.createElement('button');reset.textContent='Почати приклад спочатку';reset.addEventListener('click',()=>{caseContext.storage.reset();location.hash=record.route;location.reload();});nav.append(reset);
  document.body.prepend(banner);
  if(!location.hash)history.replaceState(null,'',location.pathname+location.search+record.route);
  return true;
}
