<template>
  <div class="flex align-items-center gap-2">
    <!-- Image preview -->
    <template v-if="isImage">
      <img :src="effectiveUrl" :alt="altText"
           style="max-width: 48px; max-height: 48px; object-fit: cover; border-radius: 4px;"/>
    </template>

    <!-- Audio controls -->
    <template v-else-if="isAudio">
      <audio :src="effectiveUrl" controls style="height: 32px"></audio>
    </template>

    <!-- File type icon -->
    <template v-else>
      <i :class="fileTypeIconClass" :style="{ color: fileTypeColor }" style="font-size: 1.5rem;"></i>
    </template>

    <!-- File info -->
    <div class="flex flex-column">
      <span class="text-sm font-medium">{{ displayName }}</span>
      <small v-if="showSize && fileSize" class="text-gray-600">{{ formattedSize }}</small>
      <small v-if="showCategory" class="text-gray-600">{{ fileTypeDisplayName }}</small>
    </div>
  </div>
</template>

<script>
import NxFileTypeManager from '@nonix-file-manager/manager/NxFileTypeManager.js'

export default {
  name: 'NxFilePreview',
  props: {
    value: {type: [String, Object], default: null},
    url: {type: String, default: ''},
    mime: {type: String, default: ''},
    title: {type: String, default: ''},
    filename: {type: String, default: ''},
    size: {type: Number, default: 0},
    urlField: {type: String, default: 'storage_url'},
    showSize: {type: Boolean, default: false},
    showCategory: {type: Boolean, default: false}
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

    // File type detection using the manager
    fileTypeInfo() {
      return NxFileTypeManager.detectFileType(this.mime, this.filename)
    },

    // File type properties from the registry
    fileTypeIconClass() {
      return NxFileTypeManager.getIconClass(this.fileTypeInfo)
    },

    fileTypeColor() {
      return NxFileTypeManager.getColor(this.fileTypeInfo)
    },

    fileTypeDisplayName() {
      return NxFileTypeManager.getDisplayName(this.fileTypeInfo)
    },

    // Check if file supports preview
    isImage() {
      return this.fileTypeInfo.category === 'image' && this.effectiveUrl
    },

    isAudio() {
      return this.fileTypeInfo.category === 'audio' && this.effectiveUrl
    },

    // Display name
    displayName() {
      return this.title || this.filename || this.fileTypeDisplayName
    },

    // Formatted file size
    formattedSize() {
      return NxFileTypeManager.formatFileSize(this.size)
    },

    // File size from props or value object
    fileSize() {
      if (this.size) return this.size
      if (this.value && typeof this.value === 'object' && this.value.size_bytes) {
        return this.value.size_bytes
      }
      return 0
    },

    altText() {
      return this.title || this.filename || 'file'
    }
  }
}
</script>

<style scoped>
</style>


