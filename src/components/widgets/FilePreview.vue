<template>
  <div class="flex align-items-center gap-2">
    <template v-if="isImage">
      <img :src="url" :alt="altText" style="max-width: 64px; max-height: 64px; object-fit: cover;" />
    </template>
    <template v-else-if="isAudio">
      <audio :src="url" controls style="height: 28px"></audio>
    </template>
    <template v-else>
      <i class="pi pi-file"></i>
    </template>
    <span class="text-sm">{{ titleOrName }}</span>
  </div>
  </template>

<script>
export default {
  name: 'FilePreview',
  props: {
    value: { type: [String, Object], default: null },
    url: { type: String, default: '' },
    mime: { type: String, default: '' },
    title: { type: String, default: '' },
    filename: { type: String, default: '' }
  },
  computed: {
    isImage() { return (this.mime || '').startsWith('image/') || (this.url && this.url.match(/\.(png|jpe?g|gif|webp|svg)$/i)) },
    isAudio() { return (this.mime || '').startsWith('audio/') || (this.url && this.url.match(/\.(mp3|wav|aac|ogg)$/i)) },
    altText() { return this.title || this.filename || 'media' },
    titleOrName() { return this.title || this.filename || this.url || '' }
  }
}
</script>

<style scoped>
</style>


