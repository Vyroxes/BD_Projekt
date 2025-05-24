import { defineConfig, searchForWorkspaceRoot } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['ip8.vp2.titanaxe.com'],
    allow: [
      searchForWorkspaceRoot(process.cwd()),
      '/home/BD_Projekt/.env',
    ],
  },
});