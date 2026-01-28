import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/customer': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/company': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/items': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/parties': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/invoice': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/payments': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/staff': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
    },
  },
})