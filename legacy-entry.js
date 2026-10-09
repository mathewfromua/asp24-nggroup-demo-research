// Preserve existing public hash links without loading the catalog on the report hub.
if (/^#\/(asp|ng)\//.test(location.hash)) location.replace('./demo.html'+location.search+location.hash);
