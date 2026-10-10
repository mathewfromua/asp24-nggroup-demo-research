import type {Product, Project} from '../domain/types.ts';
import {products} from '../data/catalog.ts';
import {isRecord, unsafeKeys} from '../domain/validation.ts';
import {SCIENCE_LIMITS, checkedProject, cleanProject} from '../domain/projects.ts';

/** The accepted version-1 interchange format remains byte-compatible. */
export function exportProject(project: Project): string {
  return JSON.stringify({format:'perspektyva-project',version:1,project:cleanProject(project)},null,2);
}
export function importProject(text: string, size: number, catalog: readonly Product[] = products): Project {
  const bytes=new TextEncoder().encode(String(text)).length;
  if(typeof text!=='string'||!Number.isFinite(size)||size<0||size>SCIENCE_LIMITS.importBytes||bytes>SCIENCE_LIMITS.importBytes) throw new Error('JSON-файл має бути не більшим за 256 КБ.');
  let payload: unknown;
  try{payload=JSON.parse(text.replace(/^\uFEFF/,''),(key,value: unknown)=>{if(unsafeKeys.has(key))throw new Error('special');return value;});}catch{throw new Error('Неприпустимий JSON або службові ключі.');}
  if(!isRecord(payload)||payload.format!=='perspektyva-project'||payload.version!==1)throw new Error('Потрібен формат perspektyva-project, версія 1.');
  return cleanProject(checkedProject(payload.project,catalog));
}
