import {isIsoTimestamp} from '../../validation.js';
import {products, money, reelLength} from '../data/catalog.ts';
import type {Product, Project, ProjectReference, ScienceState} from './types.ts';
import {isRecord, hasUnsafeKeys, cloneJson} from './validation.ts';

export const SCIENCE_LIMITS = Object.freeze({projects:30,candidates:64,references:30,name:100,note:1500,title:160,url:1000,quantity:999,importBytes:262144});
const known = (catalog: readonly Product[], id: unknown): id is string => typeof id === 'string' && catalog.some(p => p.id === id);
export const validProjectQuantity = (q: unknown): q is number => typeof q === 'number' && Number.isInteger(q) && q >= 1 && q <= SCIENCE_LIMITS.quantity;
const validId = (id: unknown): id is string => typeof id === 'string' && /^project-[1-9]\d{0,8}$/.test(id);
export const projectIdList = (ids: unknown, catalog: readonly Product[]): ids is string[] => Array.isArray(ids) && ids.length <= SCIENCE_LIMITS.candidates && new Set(ids).size === ids.length && ids.every(id => known(catalog,id));

export function safeReferenceUrl(value: unknown, catalog: readonly Product[] = products): boolean {
  if(typeof value !== 'string' || value.length > SCIENCE_LIMITS.url) return false;
  const local = /^#\/(asp|ng)\/(product|document)\/([a-z0-9-]+)$/.exec(value);
  if(local){const p=catalog.find(p=>p.id===local[3]);return !!p&&(local[1]!=='ng'||p.ng)&&(local[2]!=='document'||(local[1]==='ng'&&p.ng));}
  try {const u=new URL(value);return u.protocol==='https:' && !u.username && !u.password && !!u.hostname;} catch{return false;}
}
/** Validate first; callers commit a whole next project only after success. */
export function validateProject(value: unknown, catalog: readonly Product[] = products): string | null {
  if(!isRecord(value) || hasUnsafeKeys(value)) return 'Неприпустима структура проєкту.';
  if(!validId(value.id)) return 'Неприпустимий ідентифікатор проєкту.';
  if(typeof value.name!=='string' || !value.name.trim() || value.name.length>SCIENCE_LIMITS.name) return 'Назва має містити 1–100 символів.';
  if(typeof value.note!=='string' || value.note.length>SCIENCE_LIMITS.note) return 'Примітка має містити до 1500 символів.';
  const {candidates, chosen, quantities, references} = value;
  if(Array.isArray(candidates)&&candidates.length>SCIENCE_LIMITS.candidates) return 'До 64 кандидатів у проєкті. Поточний склад не змінено.';
  if(!projectIdList(candidates,catalog) || !projectIdList(chosen,catalog) || chosen.some(id=>!candidates.includes(id))) return 'Кандидати або вибрані моделі не відповідають каталогу.';
  if(!isRecord(quantities) || Object.keys(quantities).some(id=>!candidates.includes(id)) || candidates.some(id=>!validProjectQuantity(quantities[id]))) return 'Кількість кожного кандидата: ціле число від 1 до 999.';
  if(!Array.isArray(references) || references.length>SCIENCE_LIMITS.references || references.some(r=>!isRecord(r)||typeof r.title!=='string'||!r.title.trim()||r.title.length>SCIENCE_LIMITS.title||!safeReferenceUrl(r.url,catalog)||(r.productId!==undefined&&(typeof r.productId!=='string'||!candidates.includes(r.productId))))) return 'Перевірте назву, адресу й модель документа.';
  if(!isIsoTimestamp(value.createdAt)||!isIsoTimestamp(value.updatedAt)) return 'Некоректний час створення або зміни.';
  return null;
}
export function checkedProject(value: unknown, catalog: readonly Product[] = products): Project {
  const error = validateProject(value, catalog);
  if (error) throw new Error(error);
  // Every actionable field has passed the runtime contract above, including IDs and units.
  return value as Project;
}
export function cleanProject(p: Project): Project {
  return {id:p.id,name:p.name,note:p.note,candidates:[...p.candidates],chosen:[...p.chosen],quantities:{...p.quantities},references:p.references.map(r=>({title:r.title,url:r.url,...(r.productId?{productId:r.productId}:{})})),createdAt:p.createdAt,updatedAt:p.updatedAt};
}
export function mergeProjectCandidates(project: Project, ids: readonly string[], catalog: readonly Product[] = products): void {
  const next={...project,candidates:[...new Set([...project.candidates,...ids])],quantities:{...project.quantities}};
  for(const id of next.candidates)if(!project.candidates.includes(id))next.quantities[id]=1;
  checkedProject(next,catalog);
  project.candidates=next.candidates;project.quantities=next.quantities;
}
export function normalizeScience(raw: unknown, catalog: readonly Product[] = products): ScienceState {
  const result: ScienceState={version:1,projects:[],activeProjectId:null,nextProjectSeq:1,quarantine:[]};
  if(raw==null || (isRecord(raw)&&!Object.keys(raw).length)) return result;
  if(!isRecord(raw)||raw.version!==1){result.quarantine.push({reason:'Невідома версія даних проєктів.',raw:cloneJson(raw)});return result;}
  if(Array.isArray(raw.quarantine)) result.quarantine=cloneJson(raw.quarantine);
  if(!Array.isArray(raw.projects)){result.quarantine.push({reason:'Список проєктів пошкоджено.',raw:cloneJson(raw)});return result;}
  const seen=new Set<string>();
  for(const value of raw.projects){
    const error=validateProject(value,catalog), id = isRecord(value) ? value.id : undefined;
    if(error || typeof id !== 'string' || seen.has(id)||result.projects.length>=SCIENCE_LIMITS.projects){result.quarantine.push({reason:error||'Повторений ID або перевищено ліміт проєктів.',raw:cloneJson(value)});continue;}
    result.projects.push(cleanProject(value as Project));seen.add(id);
  }
  const next=Math.max(0,...result.projects.map(p=>Number(p.id.slice(8))))+1;
  result.nextProjectSeq=typeof raw.nextProjectSeq==='number'&&Number.isSafeInteger(raw.nextProjectSeq)&&raw.nextProjectSeq>=next&&raw.nextProjectSeq<999999999?raw.nextProjectSeq:next;
  result.activeProjectId=typeof raw.activeProjectId==='string'&&seen.has(raw.activeProjectId)?raw.activeProjectId:result.projects[0]?.id||null;
  return result;
}
export interface ProjectInput { name?: string; note?: string; candidates?: string[]; quantities?: Record<string, number>; references?: ProjectReference[] }
export function createProject(science: ScienceState, {name='Новий проєкт',note='',candidates=[],quantities={},references=[]}: ProjectInput = {}, catalog: readonly Product[] = products, now = new Date().toISOString()): Project {
  if(science.projects.length>=SCIENCE_LIMITS.projects) throw new Error('Досягнуто межу: 30 проєктів. Відредагуйте наявний проєкт. Експорт створює резервну копію, але не звільняє місце.');
  const ids=[...new Set(candidates)].filter(id=>known(catalog,id));
  const p: Project={id:`project-${science.nextProjectSeq}`,name,note,candidates:ids,chosen:[],quantities:Object.fromEntries(ids.map(id=>[id,validProjectQuantity(quantities[id])?quantities[id]:1])),references:cloneJson(references),createdAt:now,updatedAt:now};
  checkedProject(p,catalog);
  science.nextProjectSeq++;science.projects.push(p);science.activeProjectId=p.id;return p;
}
export function duplicateProject(science: ScienceState, id: string, catalog: readonly Product[] = products, now = new Date().toISOString()): Project {
  const source=science.projects.find(p=>p.id===id);if(!source)throw new Error('Проєкт не знайдено.');
  const p=createProject(science,{...source,name:`${source.name.slice(0,92)} · копія`},catalog,now);p.chosen=[...source.chosen];return p;
}
export function projectCart(project: Project, catalog: readonly Product[] = products): Record<string, number> {
  const unavailable=project.chosen.filter(id=>!catalog.find(p=>p.id===id)?.available);
  if(unavailable.length) throw new Error('Серед вибраних моделей є недоступні. Приберіть їх із вибраного перед перенесенням.');
  return Object.fromEntries(project.chosen.map(id=>[id,project.quantities[id]]));
}
export function projectText(p: Project, catalog: readonly Product[] = products): string {
  const rows=p.candidates.map(id=>{const m=catalog.find(x=>x.id===id),q=p.quantities[id];if(!m)throw new Error('Невідома модель у проєкті.');const length=reelLength(m);return `${p.chosen.includes(id)?'[Вибрано]':'[Кандидат]'} ${m.name} · ${m.sku}\n${q} × ${m.unit} · ${money(m.price*q)}${m.group==='cable'?(length === null ? ' · Метраж не уточнено' : ` · ${q*length} м`):''}`;});
  return `${p.name}\n${p.note}\n\n${rows.join('\n\n')}\n\nДокументи\n${p.references.map(r=>`${r.title}: ${r.url}`).join('\n')}\n\nУмовний склад. Нічого не надіслано компанії.`;
}
