import {defineConfig} from 'vite';
import {resolve} from 'node:path';
import {getDeploymentConfig} from './scripts/deployment-config.mjs';

const deployment = getDeploymentConfig();

/** Compile the existing demo and the tiny report-hub redirect independently. */
export default defineConfig({
  base: deployment.BASE_PATH,
  publicDir: 'public',
  build: {
    target: 'es2022',
    outDir: 'dist',
    emptyOutDir: true,
    manifest: 'vite-manifest.json',
    cssCodeSplit: true,
    sourcemap: false,
    rolldownOptions: {
      input: {
        demo: resolve('index.html'),
        legacy: resolve('legacy-entry.js'),
        hub: resolve('hub.css'),
      },
      output: {
        hashCharacters: 'hex',
        entryFileNames: 'assets/[name]-[hash:12].js',
        chunkFileNames: 'assets/[name]-[hash:12].js',
        assetFileNames: 'assets/[name]-[hash:12][extname]',
      },
    },
  },
});
