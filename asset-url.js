/** Local public resources follow the deployment path; hash routes stay unchanged. */
export function assetUrl(path, basePath = globalThis.document?.querySelector('meta[name="app-base-path"]')?.content || '/') {
  if (!/^\/(?:[A-Za-z0-9_-]+\/)*$/.test(basePath)) throw new Error('Invalid application base path');
  const relative = String(path).replace(/^\/(?!\/)/, '');
  if (!relative || /^(?:[a-z][a-z\d+.-]*:|\/)/i.test(relative) || relative.split('/').some(part => part === '..' || part === '.') || /[\\?#\s]/.test(relative)) {
    throw new Error('Expected a local asset path');
  }
  return basePath + relative;
}
