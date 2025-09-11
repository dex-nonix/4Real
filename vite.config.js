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
      '@nonix-music-artist': resolve(__dirname, 'vue_libs/nonix-music-artist'),
      '@nonix-template': resolve(__dirname, 'vue_libs/nonix-template'),
      '@nonix-dynamic': resolve(__dirname, 'vue_libs/nonix-dynamic'),
      '@nonix-menu-item': resolve(__dirname, 'vue_libs/nonix-menu-item'),
      '@nonix-voice-input': resolve(__dirname, 'vue_libs/nonix-voice-input'),
      '@nonix-crud': resolve(__dirname, 'vue_libs/nonix-crud'),
    }
  },
  optimizeDeps: {
    include: ['quill']
  },
  server: {
    allowedHosts: ['dev.local', 'localhost']
  }
})

