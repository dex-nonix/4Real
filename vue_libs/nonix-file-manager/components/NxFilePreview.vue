<template>
  <div class="flex align-items-center gap-2">
    <!-- Image preview -->
    <template v-if="isImage && effectiveUrl">
      <img :src="effectiveUrl" :alt="altText"
           style="max-width: 48px; max-height: 48px; object-fit: cover; border-radius: 4px;"/>
    </template>

    <!-- Audio controls -->
    <template v-else-if="isAudio && effectiveUrl">
      <audio :src="effectiveUrl" controls style="height: 32px"></audio>
    </template>

    <!-- File type icon with proper detection -->
    <template v-else>
      <i :class="fileTypeIconClass" :style="{ color: fileTypeColor }" style="font-size: 1.5rem;"></i>
    </template>

    <!-- File info with proper file type detection -->
    <div class="flex flex-column">
      <span class="text-sm font-medium">{{ displayName }}</span>
      <small v-if="showSize && formattedSize" class="text-gray-600">{{ formattedSize }}</small>
      <small v-if="showCategory" class="text-gray-600">{{ fileTypeDisplayName }}</small>
    </div>
  </div>
</template>

<script>
import { inject } from 'vue'

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
  setup() {
    // Inject NxFileTypeManager using Vue's dependency injection
    const fileTypeManager = inject('fileTypeManager')

    return {
      fileTypeManager
    }
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

    // Get MIME type from various sources
    mimeType() {
      if (this.mime) return this.mime
      if (this.value && typeof this.value === 'object' && this.value.mime_type) {
        return this.value.mime_type
      }
      return ''
    },

    // Get filename from various sources
    fileName() {
      if (this.filename) return this.filename
      if (this.value && typeof this.value === 'object' && this.value.original_filename) {
        return this.value.original_filename
      }
      return ''
    },

    // File type detection using injected NxFileTypeManager
    fileTypeInfo() {
      return this.fileTypeManager.detectFileType(this.mimeType, this.fileName)
    },

    // File type properties from the registry
    fileTypeIconClass() {
      return this.fileTypeManager.getIconClass(this.fileTypeInfo)
    },

    fileTypeColor() {
      return this.fileTypeManager.getColor(this.fileTypeInfo)
    },

    fileTypeDisplayName() {
      return this.fileTypeManager.getDisplayName(this.fileTypeInfo)
    },

    // Check if file supports preview based on file type category
    isImage() {
      return this.fileTypeInfo.category === 'image'
    },

    isAudio() {
      return this.fileTypeInfo.category === 'audio'
    },

    // Display name with fallback to file type name
    displayName() {
      return this.title || this.fileName || this.fileTypeDisplayName
    },

    // Formatted file size using injected NxFileTypeManager
    formattedSize() {
      const fileSize = this.size ||
        (this.value && typeof this.value === 'object' && this.value.size_bytes) ||
        0
      return fileSize > 0 ? this.fileTypeManager.formatFileSize(fileSize) : ''
    },

    altText() {
      return this.title || this.fileName || this.fileTypeDisplayName || 'file'
    }
  }
}
</script>

<style scoped>
</style>


