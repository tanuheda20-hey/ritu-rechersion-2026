import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // Allows the app to be opened through tunnelled/preview hosts
    // (e2b.app, ngrok, codespaces, localtunnel...). Dev-only convenience —
    // your production build on Vercel/Netlify is unaffected.
    allowedHosts: true,
    // Talks to the FastAPI backend in dev. Remove this block if you only
    // deploy the frontend and point VITE_API_URL at a hosted backend.
    proxy: {
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: { outDir: 'dist', sourcemap: false },
})
