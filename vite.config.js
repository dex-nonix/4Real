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
      '@nonix-advanced-layout': resolve(__dirname, 'vue_libs/nonix-advanced-layout'),
      '@nonix-file-manager': resolve(__dirname, 'vue_libs/nonix-file-manager'),
    }
  },
  optimizeDeps: {
    include: ['quill']
  },
  server: {
    allowedHosts: ['dev.local', 'localhost']
  }
})

