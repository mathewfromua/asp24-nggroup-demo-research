import {readFileSync} from 'node:fs';

export function normalizeBasePath(value) {
  const path = String(value || '/');
  const normalized = path.endsWith('/') ? path : path + '/';
  if (!/^\/(?:[A-Za-z0-9_-]+\/)*$/.test(normalized)) throw new Error('BASE_PATH must be / or an absolute directory path');
  return normalized;
}

/** The checked-in configuration is the single default; environment overrides are explicit. */
export function getDeploymentConfig(env = process.env) {
  const defaults = JSON.parse(readFileSync(new URL('../deployment.config.json', import.meta.url), 'utf8'));
  const publicUrl = new URL(env.PUBLIC_BASE_URL || defaults.PUBLIC_BASE_URL);
  if (publicUrl.protocol !== 'https:' || publicUrl.username || publicUrl.password || publicUrl.search || publicUrl.hash) {
    throw new Error('PUBLIC_BASE_URL must be a credential-free HTTPS directory URL');
  }
  const basePath = normalizeBasePath(env.BASE_PATH || (env.PUBLIC_BASE_URL ? publicUrl.pathname : defaults.BASE_PATH));
  if (env.BASE_PATH && !env.PUBLIC_BASE_URL) publicUrl.pathname = basePath;
  if (normalizeBasePath(publicUrl.pathname) !== basePath) throw new Error('PUBLIC_BASE_URL pathname and BASE_PATH disagree');
  publicUrl.pathname = basePath;
  return {PUBLIC_BASE_URL: publicUrl.href, BASE_PATH: basePath};
}
