<template>
  <Card v-if="useCard && selectedFile" class="h-full">
    <template #title>
      <div class="flex justify-content-between align-items-center">
        <span class="text-lg font-medium">{{ selectedFile.title || selectedFile.original_filename }}</span>
        <Button
          icon="pi pi-times"
          size="small"
          text
          rounded
          @click="$emit('close')"
          v-tooltip="'Close Preview'"
          class="ml-2"
        />
      </div>
    </template>

    <div class="flex flex-column gap-3">
      <!-- Image Preview -->
      <div v-if="isImage && previewUrl" class="image-preview">
        <img :src="previewUrl" :alt="selectedFile.title || selectedFile.original_filename" />
      </div>

      <!-- Audio Preview -->
      <div v-else-if="isAudio && previewUrl" class="audio-preview">
        <audio :src="previewUrl" controls></audio>
      </div>

      <!-- Video Preview (future) -->
      <div v-else-if="isVideo && previewUrl" class="video-preview">
        <video :src="previewUrl" controls style="max-width: 100%; max-height: 200px;"></video>
      </div>

      <!-- File Icon for other types -->
      <div v-else class="file-icon-preview">
        <NxFilePreview
          :value="selectedFile"
          :showSize="true"
          :showCategory="true"
          style="font-size: 3rem;"
        />
      </div>

      <!-- File Details -->
      <div class="file-details">
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
        <div v-if="selectedFile.width && selectedFile.height" class="detail-row">
          <strong>Dimensions:</strong>
          <span>{{ selectedFile.width }} × {{ selectedFile.height }}</span>
        </div>

        <!-- Duration if available -->
        <div v-if="selectedFile.duration_seconds" class="detail-row">
          <strong>Duration:</strong>
          <span>{{ formatDuration(selectedFile.duration_seconds) }}</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-wrap gap-2">
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
  </Card>

  <div v-else-if="selectedFile" class="flex flex-column h-full surface-card border-round-lg">
    <div class="flex justify-content-between align-items-center p-3 border-bottom-1 surface-border bg-surface-section border-round-top-lg">
      <span class="text-lg font-medium">{{ selectedFile.title || selectedFile.original_filename }}</span>
      <Button
        icon="pi pi-times"
        size="small"
        text
        rounded
        @click="$emit('close')"
        v-tooltip="'Close Preview'"
        class="ml-2"
      />
    </div>

    <div class="flex flex-column gap-3 p-3 overflow-y-auto">
      <!-- Image Preview -->
      <div v-if="isImage && previewUrl" class="image-preview">
        <img :src="previewUrl" :alt="selectedFile.title || selectedFile.original_filename" />
      </div>

      <!-- Audio Preview -->
      <div v-else-if="isAudio && previewUrl" class="audio-preview">
        <audio :src="previewUrl" controls></audio>
      </div>

      <!-- Video Preview (future) -->
      <div v-else-if="isVideo && previewUrl" class="video-preview">
        <video :src="previewUrl" controls style="max-width: 100%; max-height: 200px;"></video>
      </div>

      <!-- File Icon for other types -->
      <div v-else class="file-icon-preview">
        <NxFilePreview
          :value="selectedFile"
          :showSize="true"
          :showCategory="true"
          style="font-size: 3rem;"
        />
      </div>

      <!-- File Details -->
      <div class="file-details">
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
        <div v-if="selectedFile.width && selectedFile.height" class="detail-row">
          <strong>Dimensions:</strong>
          <span>{{ selectedFile.width }} × {{ selectedFile.height }}</span>
        </div>

        <!-- Duration if available -->
        <div v-if="selectedFile.duration_seconds" class="detail-row">
          <strong>Duration:</strong>
          <span>{{ formatDuration(selectedFile.duration_seconds) }}</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-wrap gap-2">
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

  <div v-else class="no-selection">
    <div class="no-selection-content">
      <i class="pi pi-file" style="font-size: 3rem; color: var(--surface-border);"></i>
      <p>Select a file to preview</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, inject, defineProps, defineEmits } from 'vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Card from 'primevue/card'
import Fieldset from 'primevue/fieldset'
import NxFilePreview from './NxFilePreview.vue'

// Props
const props = defineProps({
  selectedFile: {
    type: Object,
    default: null
  },
  useCard: { type: Boolean, default: false }
})

// Emits
const emit = defineEmits(['close', 'file-action', 'file-renamed'])

// Services
const fileTypeManager = inject('fileTypeManager')
const fileOperationsService = inject('fileOperations')

// Reactive state
const showRenameDialog = ref(false)
const newTitle = ref('')
const renaming = ref(false)

// Computed
const previewUrl = computed(() => {
  if (!props.selectedFile) return ''
  return props.selectedFile.storage_url || ''
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
  return fileTypeManager?.formatFileSize(props.selectedFile.size_bytes) || 'Unknown'
})

const categoryName = computed(() => {
  return props.selectedFile?.category?.name || 'Uncategorized'
})

// Methods
const downloadFile = () => {
  if (previewUrl.value) {
    const link = document.createElement('a')
    link.href = previewUrl.value
    link.download = props.selectedFile.original_filename
    link.click()
  }
}

const renameFile = async () => {
  if (!newTitle.value.trim() || !props.selectedFile) return

  renaming.value = true
  try {
    const result = await fileOperationsService.renameFile(props.selectedFile.id, newTitle.value.trim())
    if (result.success) {
      emit('file-renamed', {
        fileId: props.selectedFile.id,
        newTitle: newTitle.value.trim()
      })
      showRenameDialog.value = false
    }
  } catch (error) {
    console.error('Rename file error:', error)
  } finally {
    renaming.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString()
}

const formatDuration = (seconds) => {
  if (!seconds) return 'Unknown'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// Watchers
watch(() => props.selectedFile, (newFile) => {
  if (newFile) {
    newTitle.value = newFile.title || ''
  }
}, { immediate: true })
</script>

<style scoped>

.image-preview {
  text-align: center;
  margin-bottom: 1rem;
}

.image-preview img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 4px;
}

.audio-preview, .video-preview {
  margin-bottom: 1rem;
}

.file-icon-preview {
  text-align: center;
  margin-bottom: 1rem;
}

.file-details {
  margin-bottom: 1rem;
}


.no-selection {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-selection-content {
  text-align: center;
  color: var(--text-color-secondary);
}

.no-selection-content p {
  margin: 1rem 0 0 0;
  font-size: 0.875rem;
}
</style>
