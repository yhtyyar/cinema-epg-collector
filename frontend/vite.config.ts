import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '')
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY_TARGET || 'http://localhost:8001',
          changeOrigin: true
        },
        '/static': {
          target: env.VITE_API_PROXY_TARGET || 'http://localhost:8001',
          changeOrigin: true
        }
      }
    }
  }
})
