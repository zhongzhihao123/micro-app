import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    qiankun('sub-nlp', { useDevMode: true }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3001,
    cors: true,
    origin: 'http://localhost:3001',
  },
})
