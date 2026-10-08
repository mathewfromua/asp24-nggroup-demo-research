/** Visual formatting never changes catalogue values or comparison semantics. */
export const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function readable(value) {
  const text = String(value ?? '');
  const number = /\d+(?:[.,]\d+)?(?:[\u00a0\u202f ]\d{3})*(?:[A-Za-z+])?/g;
  let out = '', at = 0;
  for (const match of text.matchAll(number)) {
    out += escapeHTML(text.slice(at, match.index));
    out += `<span class="numeric-token">${escapeHTML(match[0])}</span>`;
    at = match.index + match[0].length;
  }
  return out + escapeHTML(text.slice(at));
}
