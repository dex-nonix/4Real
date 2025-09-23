<template>
  <div class="file-view flex flex-column" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- File Preview using NxFilePreview (handles all file types) -->
    <div class="file-preview-container">
      <NxFilePreview
        :value="selectedFile"
        :showSize="false"
        :showCategory="false"
        variant="preview"
      />

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

    <!-- File Details & Actions -->
    <div class="file-details flex-1 overflow-y-auto mt-3">
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
    <div class="flex flex-wrap gap-2 mt-3 flex-shrink-0">
      <Button
        v-if="hasPreviewUrl"
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
const hasPreviewUrl = computed(() => {
  return props.selectedFile?.url || false
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
.file-preview-container {
  position: relative;
  text-align: center;
  margin-bottom: 1rem;
  min-height: 100px;
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



</style>
