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
    '/api/': {
        target: 'http://0.0.0.0:5000', // Your API server (same as Socket.IO in this case)
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ''), // Optional: If your backend API doesn't expect the /api prefix
      },
    '/socket.io': {
        target: 'http://0.0.0.0:5000', // The address of your Socket.IO server
        changeOrigin: true, // Needed for virtual hosted sites
        ws: true,           // Enable WebSocket proxying
        rewrite: (path) => path.replace(/^\/socket.io/, '/socket.io'), // This might not be strictly necessary if the paths match
      }
  }
})

