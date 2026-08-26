// Derived from the AWS WAF Analyst frontend shell.
// SPDX-License-Identifier: MIT-0
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import dns from 'node:dns';

dns.setDefaultResultOrder('ipv4first');

const apiPort = Number.parseInt(process.env.AGENTGUARD_API_PORT || '8765', 10);
if (!Number.isInteger(apiPort) || apiPort < 1024 || apiPort > 65535) {
  throw new Error('invalid local API port');
}

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': `http://localhost:${apiPort}`,
    },
  },
});
