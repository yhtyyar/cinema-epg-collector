import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '')

  // Get host and port from environment variables with fallbacks
  const host = env.VITE_HOST || 'localhost'
  const port = parseInt(env.VITE_PORT || '5173')

  return {
    plugins: [react()],
    server: {
      host,
      port,
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