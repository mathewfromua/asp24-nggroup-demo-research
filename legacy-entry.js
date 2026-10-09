// Preserve old public hash links on first load and same-document navigation.
function redirectLegacyRoute() {
  if (/^#\/(asp|ng)\//.test(location.hash)) location.replace('./demo.html'+location.search+location.hash);
}
window.addEventListener('hashchange',redirectLegacyRoute);
redirectLegacyRoute();
