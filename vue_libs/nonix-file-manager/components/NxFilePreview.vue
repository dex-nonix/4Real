<template>
  <div :class="containerClasses">
    <!-- Image preview -->
    <template v-if="isImage && effectiveUrl">
      <img :src="effectiveUrl" :alt="altText" :class="imageClasses"/>
    </template>

    <!-- Audio controls -->
    <template v-else-if="isAudio && effectiveUrl">
      <audio :src="effectiveUrl" controls :class="audioClasses"></audio>
    </template>

    <!-- Video controls -->
    <template v-else-if="isVideo && effectiveUrl">
      <video :src="effectiveUrl" controls :class="videoClasses"></video>
    </template>

    <!-- File type icon with proper detection -->
    <template v-else>
      <i :class="iconClasses" :style="{ color: fileTypeColor }"></i>
    </template>

    <!-- File info with proper file type detection -->
    <div v-if="showInfo" class="flex flex-column">
      <span class="text-sm font-medium">{{ displayName }}</span>
      <small v-if="showSize && formattedSize" class="text-color-secondary">{{ formattedSize }}</small>
      <small v-if="showCategory" class="text-color-secondary">{{ fileTypeDisplayName }}</small>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, defineProps } from 'vue'

// Props
const props = defineProps({
  value: {type: [String, Object], default: null},
  url: {type: String, default: ''},
  mime: {type: String, default: ''},
  title: {type: String, default: ''},
  filename: {type: String, default: ''},
  size: {type: Number, default: 0},
  urlField: {type: String, default: 'storage_url'},
  showSize: {type: Boolean, default: false},
  showCategory: {type: Boolean, default: false},
  variant: {type: String, default: 'thumbnail', validator: value => ['thumbnail', 'preview'].includes(value)}
})

// Services
const fileTypeManager = inject('fileTypeManager')
const fileManagerService = inject('file-manager')

// Computed
const effectiveUrl = computed(() => {
  if (props.url) return props.url
  if (typeof props.value === 'string' && props.value) return props.value
  if (props.value && typeof props.value === 'object') {
    // Use the url field directly - it's already a full URL
    if (props.value.url) return props.value.url
    // Fallback to old behavior if no url field
    if (props.value[props.urlField]) return props.value[props.urlField]
  }
  return ''
})

// Get MIME type from various sources
const mimeType = computed(() => {
  if (props.mime) return props.mime
  if (props.value && typeof props.value === 'object' && props.value.mime_type) {
    return props.value.mime_type
  }
  return ''
})

// Get filename from various sources
const fileName = computed(() => {
  if (props.filename) return props.filename
  if (props.value && typeof props.value === 'object' && props.value.original_filename) {
    return props.value.original_filename
  }
  return ''
})

// File type detection using injected NxFileTypeManager
const fileTypeInfo = computed(() => {
  return fileTypeManager.detectFileType(mimeType.value, fileName.value)
})

// File type properties from the registry
const fileTypeIconClass = computed(() => {
  return fileTypeManager.getIconClass(fileTypeInfo.value)
})

const fileTypeColor = computed(() => {
  return fileTypeManager.getColor(fileTypeInfo.value)
})

const fileTypeDisplayName = computed(() => {
  return fileTypeManager.getDisplayName(fileTypeInfo.value)
})

// Check if file supports preview based on file type category
const isImage = computed(() => {
  return fileTypeInfo.value.category === 'image'
})

const isAudio = computed(() => {
  return fileTypeInfo.value.category === 'audio'
})

const isVideo = computed(() => {
  return fileTypeInfo.value.category === 'video'
})

// Variant-based classes
const containerClasses = computed(() => {
  return props.variant === 'preview'
    ? 'flex flex-column align-items-center gap-3'
    : 'flex align-items-center gap-2'
})

const imageClasses = computed(() => {
  return props.variant === 'preview'
    ? 'max-w-full max-h-25rem border-round object-contain'
    : 'w-3rem h-3rem border-round object-cover'
})

const audioClasses = computed(() => {
  return props.variant === 'preview'
    ? 'w-full h-4rem'
    : 'h-2rem'
})

const videoClasses = computed(() => {
  return props.variant === 'preview'
    ? 'max-w-full max-h-20rem border-round object-contain'
    : 'w-3rem h-3rem border-round object-cover'
})

const iconClasses = computed(() => {
  return props.variant === 'preview'
    ? [fileTypeIconClass.value, 'text-6xl']
    : [fileTypeIconClass.value, 'text-xl']
})

const showInfo = computed(() => {
  return props.variant === 'thumbnail'
})

// Display name with fallback to file type name
const displayName = computed(() => {
  return props.title || fileName.value || fileTypeDisplayName.value
})

// Formatted file size using injected NxFileTypeManager
const formattedSize = computed(() => {
  const fileSize = props.size ||
    (props.value && typeof props.value === 'object' && props.value.size_bytes) ||
    0
  return fileSize > 0 ? fileTypeManager.formatFileSize(fileSize) : ''
})

const altText = computed(() => {
  return props.title || fileName.value || fileTypeDisplayName.value || 'file'
})
</script>

<style scoped>
</style>


