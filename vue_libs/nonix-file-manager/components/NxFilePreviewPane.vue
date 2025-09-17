<template>
  <div v-if="selectedFile" class="file-preview-pane">
    <div class="preview-header">
      <h6>File Preview</h6>
      <Button
        icon="pi pi-times"
        size="small"
        @click="$emit('close')"
        v-tooltip="'Close Preview'"
      />
    </div>

    <div class="preview-content">
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
        <div class="detail-row">
          <strong>Name:</strong>
          <span>{{ selectedFile.original_filename }}</span>
        </div>

        <div class="detail-row">
          <strong>Title:</strong>
          <span>{{ selectedFile.title || 'No title' }}</span>
        </div>

        <div class="detail-row">
          <strong>Size:</strong>
          <span>{{ formattedSize }}</span>
        </div>

        <div class="detail-row">
          <strong>Type:</strong>
          <span>{{ selectedFile.mime_type }}</span>
        </div>

        <div class="detail-row">
          <strong>Category:</strong>
          <span>{{ categoryName }}</span>
        </div>

        <div class="detail-row">
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
      <div class="preview-actions">
        <Button
          v-if="previewUrl"
          icon="pi pi-download"
          label="Download"
          size="small"
          @click="downloadFile"
        />
        <Button
          icon="pi pi-pencil"
          label="Rename"
          size="small"
          @click="showRenameDialog = true"
        />
        <Button
          icon="pi pi-copy"
          label="Copy"
          size="small"
          @click="$emit('file-action', 'copy', selectedFile)"
        />
        <Button
          icon="pi pi-arrow-right"
          label="Move"
          size="small"
          @click="$emit('file-action', 'move', selectedFile)"
        />
        <Button
          icon="pi pi-trash"
          label="Delete"
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
          label="Rename"
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

<script>
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import NxFilePreview from './NxFilePreview.vue'
import { inject } from 'vue'

export default {
  name: 'NxFilePreviewPane',
  components: {
    Button,
    Dialog,
    InputText,
    NxFilePreview
  },
  props: {
    selectedFile: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'file-action', 'file-renamed'],
  data() {
    return {
      showRenameDialog: false,
      newTitle: '',
      renaming: false
    }
  },
  computed: {
    fileTypeManager() {
      return inject('fileTypeManager')
    },

    fileOperationsService() {
      return inject('fileOperations')
    },

    previewUrl() {
      if (!this.selectedFile) return ''
      return this.selectedFile.storage_url || ''
    },

    isImage() {
      if (!this.selectedFile?.mime_type) return false
      return this.selectedFile.mime_type.startsWith('image/')
    },

    isAudio() {
      if (!this.selectedFile?.mime_type) return false
      return this.selectedFile.mime_type.startsWith('audio/')
    },

    isVideo() {
      if (!this.selectedFile?.mime_type) return false
      return this.selectedFile.mime_type.startsWith('video/')
    },

    formattedSize() {
      if (!this.selectedFile?.size_bytes) return 'Unknown'
      return this.fileTypeManager?.formatFileSize(this.selectedFile.size_bytes) || 'Unknown'
    },

    categoryName() {
      return this.selectedFile?.category?.name || 'Uncategorized'
    }
  },
  watch: {
    selectedFile: {
      handler(newFile) {
        if (newFile) {
          this.newTitle = newFile.title || ''
        }
      },
      immediate: true
    }
  },
  methods: {
    downloadFile() {
      if (this.previewUrl) {
        const link = document.createElement('a')
        link.href = this.previewUrl
        link.download = this.selectedFile.original_filename
        link.click()
      }
    },

    async renameFile() {
      if (!this.newTitle.trim() || !this.selectedFile) return

      this.renaming = true
      try {
        const result = await this.fileOperationsService.renameFile(this.selectedFile.id, this.newTitle.trim())
        if (result.success) {
          this.$emit('file-renamed', {
            fileId: this.selectedFile.id,
            newTitle: this.newTitle.trim()
          })
          this.showRenameDialog = false
        }
      } catch (error) {
        console.error('Rename file error:', error)
      } finally {
        this.renaming = false
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString()
    },

    formatDuration(seconds) {
      if (!seconds) return 'Unknown'

      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = Math.floor(seconds % 60)

      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
      }
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.file-preview-pane {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--surface-border);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid var(--surface-border);
}

.preview-header h6 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.preview-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

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

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  padding: 0.25rem 0;
  border-bottom: 1px solid var(--surface-border);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row strong {
  font-weight: 600;
  color: var(--text-color-secondary);
}

.detail-row span {
  text-align: right;
  word-break: break-word;
}

.preview-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.preview-actions .p-button {
  flex: 1;
  min-width: 80px;
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
