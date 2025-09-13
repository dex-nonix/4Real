import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import {resolve} from 'path'

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
            '@nonix': resolve(__dirname, 'vue_libs/nonix'),
            '@nonix-advanced-layout': resolve(__dirname, 'vue_libs/nonix-advanced-layout'),
            '@nonix-api': resolve(__dirname, 'vue_libs/nonix-api'),
            '@nonix-chat': resolve(__dirname, 'vue_libs/nonix-chat'),
            '@nonix-crud': resolve(__dirname, 'vue_libs/nonix-crud'),
            '@nonix-dynamic': resolve(__dirname, 'vue_libs/nonix-dynamic'),
            '@nonix-file-manager': resolve(__dirname, 'vue_libs/nonix-file-manager'),
            '@nonix-menu-item': resolve(__dirname, 'vue_libs/nonix-menu-item'),
            '@nonix-music-artist': resolve(__dirname, 'vue_libs/nonix-music-artist'),
            '@nonix-obj': resolve(__dirname, 'vue_libs/nonix-obj'),
            '@nonix-plugin': resolve(__dirname, 'vue_libs/nonix-plugin'),
            '@nonix-router': resolve(__dirname, 'vue_libs/nonix-router'),
            '@nonix-template': resolve(__dirname, 'vue_libs/nonix-template'),
            '@nonix-voice-input': resolve(__dirname, 'vue_libs/nonix-voice-input'),
            '@nonix-ws': resolve(__dirname, 'vue_libs/nonix-ws'),
        }
    },
    optimizeDeps: {
        include: ['quill']
    },
    server: {
        allowedHosts: ['dev.local', 'localhost']
    }
})

