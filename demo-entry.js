import {prepareCase} from './case-context.js';
// Start the explicitly requested workbench graph while case/session state is
// prepared. Mounting remains owned by app.js; its classic fallback handles a
// failed import. Other routes do not fetch React or the workbench styles.
if(/^#\/(asp|ng)\/compare\?/.test(location.hash)&&new URLSearchParams(location.hash.split('?')[1]).get('experience')==='modern'){
  void import('./src/ui/comparison-workbench.tsx').catch(()=>{});
}
try {
  if(await prepareCase())await import('./app.js');
} catch {
  const p=document.createElement('p');p.textContent='Не вдалося відкрити приклад. Оновіть сторінку або поверніться до оглядів.';
  const a=document.createElement('a');a.href='./';a.textContent='До оглядів';document.body.append(p,a);
}
