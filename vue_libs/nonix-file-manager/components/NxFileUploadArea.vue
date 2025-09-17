<template>
      <div class="file-upload-area">
    <!-- Upload Button (compact) -->
    <Button
      @click="$refs.fileInput.click()"
      icon="pi pi-upload"
      size="small"
      outlined
      class="upload-button"
      :disabled="!categoryId"
      v-tooltip.left="categoryId ? 'Upload Files' : 'Select a category first'"
    />

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      multiple
      style="display: none"
      @change="handleFileSelect"
    />

    <!-- Upload Progress (when uploading) -->
    <div v-if="uploading" class="upload-progress-overlay">
      <div class="upload-progress-card">
        <div class="progress-header">
          <i class="pi pi-upload"></i>
          <span>Uploading {{ currentFileName }}</span>
        </div>
        <ProgressBar :value="uploadProgress" class="upload-progress-bar" />
        <div class="progress-text">{{ uploadProgress }}%</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, defineProps, defineEmits } from 'vue'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'

// Props
const props = defineProps({
  categoryId: {
    type: [Number, String],
    default: null
  }
})

// Emits
const emit = defineEmits(['file-uploaded'])

// Services
const fileService = inject('files')

// Reactive state
const uploading = ref(false)
const uploadProgress = ref(0)
const currentFileName = ref('')

// Methods
const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  if (files.length === 0) return

  // Reset input
  event.target.value = ''

  // Upload files sequentially
  uploadFiles(files)
}

const uploadFiles = async (files) => {
  for (const file of files) {
    await uploadFile(file)
  }
}

const uploadFile = async (file) => {
  if (!props.categoryId) {
    console.error('No category selected for upload')
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  currentFileName.value = file.name

  try {
    const result = await fileService.create({
      upload: file,
      title: file.name,
      category_id: props.categoryId
    }, {
      onProgress: (progress) => {
        uploadProgress.value = progress
      }
    })

    // Backend returns {data: {data: [...], pagination: {...}}}
    const uploadedFile = result.data?.data || result.data
    if (uploadedFile) {
      emit('file-uploaded', uploadedFile)
    }
  } catch (error) {
    console.error('Upload failed:', error)
    // Could emit error event here
  } finally {
    uploading.value = false
    uploadProgress.value = 0
    currentFileName.value = ''
  }
}
</script>

<style scoped>
.file-upload-area {
  position: relative;
  display: inline-block;
}

.upload-button {
  border-style: dashed;
  border-width: 1px;
  transition: all 0.2s;
}

.upload-button:hover {
  background-color: var(--primary-50);
  border-color: var(--primary-300);
}

.upload-progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.upload-progress-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  text-align: center;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.progress-header i {
  color: var(--primary-500);
  font-size: 1.2rem;
}

.progress-header span {
  font-weight: 500;
  color: var(--text-color);
}

.upload-progress-bar {
  margin-bottom: 0.5rem;
}

.progress-text {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}
</style>
