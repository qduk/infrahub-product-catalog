/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The browser only talks to this app's origin. In development, /api goes to the catalog service.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8200',
    },
  },
  test: {
    environment: 'jsdom',
  },
})
