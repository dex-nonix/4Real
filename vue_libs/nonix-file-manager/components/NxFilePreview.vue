<template>
  <div class="flex align-items-center gap-2">
    <template v-if="isImage">
      <img :src="effectiveUrl" :alt="altText" style="max-width: 64px; max-height: 64px; object-fit: cover;"/>
    </template>
    <template v-else-if="isAudio">
      <audio :src="effectiveUrl" controls style="height: 28px"></audio>
    </template>
    <template v-else>
      <i class="pi pi-file"></i>
    </template>
    <span class="text-sm">{{ titleOrName }}</span>
  </div>
</template>

<script>
export default {
  name: 'NxFilePreview',
  props: {
    value: {type: [String, Object], default: null},
    url: {type: String, default: ''},
    mime: {type: String, default: ''},
    title: {type: String, default: ''},
    filename: {type: String, default: ''},
    urlField: {type: String, default: 'storage_url'}
  },
  computed: {
    effectiveUrl() {
      if (this.url) return this.url
      if (typeof this.value === 'string' && this.value) return this.value
      if (this.value && typeof this.value === 'object') {
        if (this.value[this.urlField]) return this.value[this.urlField]
      }
      return ''
    },
    isImage() {
      return (this.mime || '').startsWith('image/') || (this.effectiveUrl && this.effectiveUrl.match(/\.(png|jpe?g|gif|webp|svg)$/i))
    },
    isAudio() {
      return (this.mime || '').startsWith('audio/') || (this.effectiveUrl && this.effectiveUrl.match(/\.(mp3|wav|aac|ogg)$/i))
    },
    altText() {
      return this.title || this.filename || 'media'
    },
    titleOrName() {
      return this.title || this.filename || this.effectiveUrl || ''
    }
  }
}
</script>

<style scoped>
</style>


