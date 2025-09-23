<template>
  <div class="file-view" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- Image Preview with Overlay Maximize Button -->
    <div v-if="isImage && previewUrl" class="image-preview-container">
      <img :src="previewUrl" :alt="selectedFile.title || selectedFile.original_filename"
           :style="imageStyle" />

      <!-- Overlay Maximize Button -->
      <Button
        icon="pi pi-expand"
        class="maximize-overlay-btn"
        text
        rounded
        size="small"
        v-tooltip="maximizeTooltip"
        @click="handleMaximize"
      />
    </div>

    <!-- Audio Preview -->
    <div v-else-if="isAudio && previewUrl" class="audio-preview">
      <audio :src="previewUrl" controls :style="mediaStyle"></audio>
    </div>

    <!-- Video Preview with Overlay -->
    <div v-else-if="isVideo && previewUrl" class="video-preview-container">
      <video :src="previewUrl" controls :style="mediaStyle"></video>

      <!-- Overlay Maximize Button -->
      <Button
        icon="pi pi-expand"
        class="maximize-overlay-btn"
        text
        rounded
        size="small"
        v-tooltip="maximizeTooltip"
        @click="handleMaximize"
      />
    </div>

    <!-- File Icon for other types -->
    <div v-else class="file-icon-preview">
      <NxFilePreview :value="selectedFile" :showSize="true" :showCategory="true"
                    :style="{ fontSize: isFullscreen ? '5rem' : '3rem' }" />
    </div>

    <!-- File Details & Actions -->
    <div class="file-details mt-3">
      <div class="flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border">
        <strong>Name:</strong>
        <span>{{ selectedFile.original_filename }}</span>
      </div>

      <div class="flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border">
        <strong>Title:</strong>
        <span>{{ selectedFile.title || 'No title' }}</span>
      </div>

      <div class="flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border">
        <strong>Size:</strong>
        <span>{{ formattedSize }}</span>
      </div>

      <div class="flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border">
        <strong>Type:</strong>
        <span>{{ selectedFile.mime_type }}</span>
      </div>

      <div class="flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border">
        <strong>Category:</strong>
        <span>{{ categoryName }}</span>
      </div>

      <div class="flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border">
        <strong>Created:</strong>
        <span>{{ formatDate(selectedFile.created_at) }}</span>
      </div>

      <!-- Image dimensions if available -->
      <div v-if="selectedFile.width && selectedFile.height" class="flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border">
        <strong>Dimensions:</strong>
        <span>{{ selectedFile.width }} × {{ selectedFile.height }}</span>
      </div>

      <!-- Duration if available -->
      <div v-if="selectedFile.duration_seconds" class="flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border">
        <strong>Duration:</strong>
        <span>{{ formatDuration(selectedFile.duration_seconds) }}</span>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-wrap gap-2 mt-3">
      <Button
        v-if="previewUrl"
        icon="pi pi-download"
        text rounded v-tooltip.top="'Download'"
        size="small"
        @click="downloadFile"
      />
      <Button
        icon="pi pi-pencil"
        text rounded v-tooltip.top="'Rename'"
        size="small"
        @click="showRenameDialog = true"
      />
      <Button
        icon="pi pi-copy"
        text rounded v-tooltip.top="'Copy'"
        size="small"
        @click="$emit('file-action', 'copy', selectedFile)"
      />
      <Button
        icon="pi pi-arrow-right"
        text rounded v-tooltip.top="'Move'"
        size="small"
        @click="$emit('file-action', 'move', selectedFile)"
      />
      <Button
        icon="pi pi-trash"
        text rounded v-tooltip.top="'Delete'"
        size="small"
        severity="danger"
        @click="$emit('file-action', 'delete', selectedFile)"
      />
    </div>

    <!-- Rename Dialog -->
    <Dialog
      v-model:visible="showRenameDialog"
      modal
      header="Rename File"
      :style="{ width: '400px' }"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="fileTitle">Title</label>
          <InputText
            id="fileTitle"
            v-model="newTitle"
            @keyup.enter="renameFile"
          />
        </div>
      </div>
      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="showRenameDialog = false"
        />
        <Button
          text rounded v-tooltip.top="'Rename'"
          icon="pi pi-check"
          :loading="renaming"
          @click="renameFile"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import NxFilePreview from './NxFilePreview.vue'
import { downloadFile, formatDate, formatDuration } from '../utils/index.js'

// Props
const props = defineProps({
  selectedFile: { type: Object, required: true },
  maximizeMode: {
    type: String,
    default: 'dialog', // 'dialog' or 'fullscreen'
    validator: value => ['dialog', 'fullscreen'].includes(value)
  }
})

// Emits
const emit = defineEmits(['open-fullscreen-dialog', 'file-action', 'file-renamed'])

// Reactive state
const showRenameDialog = ref(false)
const newTitle = ref('')
const renaming = ref(false)
const isFullscreen = ref(false)

// Computed
const previewUrl = computed(() => {
  if (!props.selectedFile) return ''
  return props.selectedFile.url || ''
})

const isImage = computed(() => {
  if (!props.selectedFile?.mime_type) return false
  return props.selectedFile.mime_type.startsWith('image/')
})

const isAudio = computed(() => {
  if (!props.selectedFile?.mime_type) return false
  return props.selectedFile.mime_type.startsWith('audio/')
})

const isVideo = computed(() => {
  if (!props.selectedFile?.mime_type) return false
  return props.selectedFile.mime_type.startsWith('video/')
})

const formattedSize = computed(() => {
  if (!props.selectedFile?.size_bytes) return 'Unknown'
  // Use a simple formatter for now - will integrate with fileTypeManager later
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (props.selectedFile.size_bytes === 0) return '0 Bytes'
  const i = parseInt(Math.floor(Math.log(props.selectedFile.size_bytes) / Math.log(1024)))
  return Math.round(props.selectedFile.size_bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
})

const categoryName = computed(() => {
  return props.selectedFile?.category?.name || 'Uncategorized'
})

const imageStyle = computed(() => ({
  maxWidth: '100%',
  maxHeight: isFullscreen.value ? '70vh' : (props.maximizeMode === 'fullscreen' ? '60vh' : '200px'),
  objectFit: 'contain',
  borderRadius: '4px'
}))

const mediaStyle = computed(() => ({
  width: isFullscreen.value ? '100%' : 'auto',
  maxHeight: isFullscreen.value ? '65vh' : (props.maximizeMode === 'fullscreen' ? '50vh' : '200px')
}))

const maximizeTooltip = computed(() => {
  if (props.maximizeMode === 'dialog') {
    return 'Open in Fullscreen Dialog'
  }
  return isFullscreen.value ? 'Minimize' : 'Maximize to Full Browser'
})

// Methods
const handleMaximize = () => {
  if (props.maximizeMode === 'dialog') {
    // Emit to open fullscreen dialog
    emit('open-fullscreen-dialog')
  } else {
    // Toggle fullscreen mode
    isFullscreen.value = !isFullscreen.value
  }
}

const downloadFileLocal = () => {
  downloadFile(props.selectedFile)
}

const renameFile = async () => {
  if (!newTitle.value.trim() || !props.selectedFile) return

  renaming.value = true
  try {
    // For now, emit the rename event - will be handled by parent
    emit('file-renamed', {
      fileId: props.selectedFile.id,
      newTitle: newTitle.value.trim()
    })
    showRenameDialog.value = false
  } catch (error) {
    console.error('Rename file error:', error)
  } finally {
    renaming.value = false
  }
}

// Watch for file changes to reset title
import { watch } from 'vue'
watch(() => props.selectedFile, (newFile) => {
  if (newFile) {
    newTitle.value = newFile.title || ''
  }
}, { immediate: true })
</script>

<style scoped>
.image-preview-container, .video-preview-container {
  position: relative;
  text-align: center;
  margin-bottom: 1rem;
  max-height: 200px;
  overflow: visible;
}

.maximize-overlay-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0.9;
  transition: opacity 0.2s;
  z-index: 10;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.maximize-overlay-btn:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.9);
}

.image-preview, .audio-preview, .video-preview, .file-icon-preview {
  text-align: center;
}

.file-details {
  margin-bottom: 1rem;
}

.fullscreen-mode .file-icon-preview {
  /* Additional fullscreen styling if needed */
}
</style>
