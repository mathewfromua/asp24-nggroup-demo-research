import {prepareCase} from './case-context.js';
try {
  if(await prepareCase())await import('./app.js');
} catch {
  const p=document.createElement('p');p.textContent='Не вдалося відкрити приклад. Оновіть сторінку або поверніться до оглядів.';
  const a=document.createElement('a');a.href='./';a.textContent='До оглядів';document.body.append(p,a);
}
