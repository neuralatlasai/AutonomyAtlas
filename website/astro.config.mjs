import { defineConfig } from 'astro/config';
import preact from '@astrojs/preact';

export default defineConfig({
  site: 'https://neuralatlasai.github.io',
  base: '/AutonomyAtlas',
  output: 'static',
  trailingSlash: 'always',
  integrations: [preact()],
  server: { host: '127.0.0.1', port: 4173 },
});
