<template>
  <div class="flex flex-column h-full">
    <!-- Toolbar using PrimeVue Toolbar component -->
    <Toolbar class="">
      <template #start>
        <div class="flex align-items-center gap-2">
          <Dropdown
            v-if="isMobile"
            v-model="selectedCategoryId"
            :options="[{ id: null, name: 'All' }, ...(categories || [])]"
            optionLabel="name"
            optionValue="id"
            placeholder="Category"
            @change="handleCategoryChange"
            class="w-8rem"
            size="small"
          />
          <Button
            @click="layout = 'list'"
            :outlined="viewMode !== 'list'"
            icon="pi pi-list"
            size="small"
            v-tooltip.bottom="'List View'"
          />
          <Button
            @click="layout = 'grid'"
            :outlined="viewMode !== 'grid'"
            icon="pi pi-th"
            size="small"
            v-tooltip.bottom="'Grid View'"
          />
        </div>
      </template>
      
      <template #center>
        <span class="text-sm text-color-secondary">{{ files.length }} files</span>
      </template>
      
      <template #end>
        <NxFileUploadArea
          v-if="allowUpload"
          :categoryId="selectedCategories[0]"
          @file-uploaded="handleFileUploaded"
        />
      </template>
    </Toolbar>
    
    <DataView
      :value="files"
      :layout="viewMode"
      :loading="loading"
      :paginator="true"
      :rows="gridPageSize"
      class="h-full"
      v-model:selection="selectedFilesLocal"
      selectionMode="multiple"
    >

      <!-- List View Template -->
      <template #list="slotProps">
        <div class="flex flex-column">
          <div v-for="(item, index) in slotProps.items" :key="index">
            <div class="flex flex-column sm:flex-row sm:align-items-center p-4 gap-3" 
                :class="{ 'border-top-1 surface-border': index !== 0, 'bg-primary-50 border-primary': isSelected(item) }"
                @click="selectFile(item)"
                @dblclick="openFile(item)"
                style="cursor: pointer"
            >
              <div class="relative">
                <NxFilePreview
                  :value="item"
                  :showSize="true"
                  :showCategory="true"
                />
              </div>
              <div class="flex flex-column md:flex-row justify-content-between md:align-items-center flex-1 gap-3">
                <div class="flex flex-column gap-2">
                  <div class="text-lg font-medium">{{ item.original_filename }}</div>
                  <div class="flex gap-2">
                    <span class="text-color-secondary">{{ formattedSize(item.size_bytes) }}</span>
                    <span class="text-color-secondary">{{ item.mime_type }}</span>
                  </div>
                </div>
                <div class="flex gap-2">
                  <Button icon="pi pi-eye" size="small" text rounded v-tooltip.top="'View File'" @click.stop="openFile(item)" />
                  <Button icon="pi pi-trash" size="small" text rounded severity="danger" v-tooltip.top="'Delete File'" @click.stop="handleRowAction('delete', item)" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Grid View Template -->
      <template #grid="slotProps">
        <div class="grid">
          <div v-for="(item, index) in slotProps.items" :key="index" class="col-12 sm:col-6 md:col-4 lg:col-3 xl:col-2 p-2">
            <div class="surface-card border-1 surface-border border-round-lg p-3 cursor-pointer transition-all transition-duration-200 flex flex-column align-items-center text-center" 
              :class="{ 'border-primary bg-primary-50': isSelected(item) }"
              style="aspect-ratio: 1"
              @click="selectFile(item)"
              @dblclick="openFile(item)"
            >
              <div class="mb-2">
                <NxFilePreview
                  :value="item"
                  :showSize="true"
                  :showCategory="true"
                />
              </div>
              <div class="w-full">
                <div class="text-sm font-medium mb-1 break-word line-height-2">{{ item.original_filename ? truncateFileName(item.original_filename) : 'Untitled' }}</div>
                <div class="text-color-secondary">{{ item.size_bytes ? formattedSize(item.size_bytes) : '' }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </DataView>
    
    <!-- Bulk Actions (shown when files selected) -->
    <div v-if="selectedFilesLocal.length > 0" class="flex justify-content-between align-items-center p-3 surface-section border-top-1 surface-border flex-shrink-0">
      <div class="text-sm text-color-secondary">
        {{ selectedFilesLocal.length }} file{{ selectedFilesLocal.length > 1 ? 's' : '' }} selected
      </div>
      <div class="flex gap-2">
        <Button
          @click="handleBulkAction('copy')"
          icon="pi pi-copy"
          size="small"
          text
          rounded
          v-tooltip.top="'Copy selected files'"
        />
        <Button
          @click="handleBulkAction('move')"
          icon="pi pi-arrow-right"
          size="small"
          text
          rounded
          v-tooltip.top="'Move selected files'"
        />
        <Button
          @click="handleBulkAction('delete')"
          icon="pi pi-trash"
          size="small"
          text
          rounded
          severity="danger"
          v-tooltip.top="'Delete selected files'"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, inject, defineProps, defineEmits } from 'vue'
import DataView from 'primevue/dataview'
import Button from 'primevue/button'
import Toolbar from 'primevue/toolbar'
import Dropdown from 'primevue/dropdown'
import NxFilePreview from './NxFilePreview.vue'
import NxFileUploadArea from './NxFileUploadArea.vue'

// Props
const props = defineProps({
  files: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  viewMode: {
    type: String,
    default: 'list',
    validator: value => ['list', 'grid'].includes(value)
  },
  selectionMode: {
    type: String,
    default: 'multiple',
    validator: value => ['single', 'multiple'].includes(value)
  },
  selectedFiles: {
    type: Array,
    default: () => []
  },
  selectedCategories: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  },
  isMobile: {
    type: Boolean,
    default: false
  },
  allowUpload: {
    type: Boolean,
    default: true
  },
  gridPageSize: {
    type: Number,
    default: 20
  }
})

// Emits
const emit = defineEmits(['update:selectedFiles', 'row-action', 'bulk-action', 'upload', 'view-mode-change', 'file-select', 'file-open', 'file-uploaded', 'category-select'])

// Services
const fileTypeManager = inject('fileTypeManager')

// Reactive state
const selectedFilesLocal = ref([...props.selectedFiles])
const layout = ref(props.viewMode)
const selectedCategoryId = ref(null)

// Watchers
watch(() => props.selectedFiles, (newVal) => {
  selectedFilesLocal.value = [...newVal]
}, { immediate: true })

watch(selectedFilesLocal, (newVal) => {
  emit('update:selectedFiles', newVal)
})

watch(layout, (newVal) => {
  emit('view-mode-change', newVal)
})

// Methods
const selectFile = (file) => {
  const alreadySelected = isSelected(file)
  if (alreadySelected) {
    selectedFilesLocal.value = selectedFilesLocal.value.filter(f => f.id !== file.id)
  } else {
    selectedFilesLocal.value = [...selectedFilesLocal.value, file]
  }
  emit('file-select', file)
}

const openFile = (file) => {
  emit('file-open', file)
}

const isSelected = (file) => {
  return selectedFilesLocal.value.some(f => f.id === file.id)
}

const handleRowAction = (action, rowData) => {
  emit('row-action', { action, rowData })
}

const handleBulkAction = (action) => {
  emit('bulk-action', {
    action,
    selectedFiles: selectedFilesLocal.value
  })
}

const handleFileUploaded = (uploadedFile) => {
  // Emit the uploaded file to parent
  emit('file-uploaded', uploadedFile)
}

const truncateFileName = (filename) => {
  if (!filename) return ''
  if (filename.length <= 20) return filename
  return filename.substring(0, 17) + '...'
}

const handleCategoryChange = (event) => {
  emit('category-select', event.value)
}

const formattedSize = (bytes) => {
  if (!bytes) return ''
  return fileTypeManager?.formatFileSize(bytes) || ''
}
</script>

<style scoped>
/* Responsive adjustments */
@media (max-width: 768px) {
  /* Add any mobile-specific styles here */
}
</style>
