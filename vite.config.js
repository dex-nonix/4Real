import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@nonix': resolve(__dirname, 'vue_libs/nonix'),
      '@nonix-chat': resolve(__dirname, 'vue_libs/nonix-chat'),
      '@nonix-master-layout': resolve(__dirname, 'vue_libs/nonix-master-layout'),
    }
  },
  optimizeDeps: {
    include: ['quill']
  },
  server: {
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
})

