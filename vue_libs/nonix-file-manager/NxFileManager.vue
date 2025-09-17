<template>
  <div class="file-manager" :class="{ 'mobile': isMobile, 'compact': compact }" :style="{ height: height }">
    <template v-if="useSplitter">
      <Splitter
        v-if="!isMobile"
        :gutterSize="8"
        class="file-manager-splitter"
      >
      <!-- Sidebar Tree -->
      <SplitterPanel v-if="showTree" :size="sidebarWidth" :minSize="5">
        <NxFileTree
          v-model:selectedCategories="selectedCategories"
          :categories="categories"
          :selectionMode="selectionMode"
          :hierarchical="hierarchical"
          :showCounts="showCounts"
          :treeData="treeData"
          :allowCreate="allowCreateCategory"
          @category-select="handleCategorySelect"
          @category-unselect="handleCategoryUnselect"
          @category-created="handleCategoryCreated"
        />
      </SplitterPanel>

      <!-- Main Content Area -->
      <SplitterPanel :size="100 - sidebarWidth" :minSize="50">
        <Splitter orientation="vertical">
          <!-- File List -->
          <SplitterPanel :size="previewHeight" :minSize="40">
            <NxFileListView
              :files="filteredFiles"
              :loading="loading"
              :viewMode="viewMode"
              :selectionMode="selectionMode"
              :selectedFiles.sync="selectedFiles"
              :selectedCategories="selectedCategories"
              :allowUpload="allowUpload"
              @row-action="handleFileAction"
              @bulk-action="handleBulkAction"
              @view-mode-change="handleViewModeChange"
              @file-select="handleFileSelect"
              @file-open="handleFileOpen"
              @file-uploaded="handleFileUploaded"
            />
          </SplitterPanel>

          <!-- Preview Pane -->
          <SplitterPanel
            v-if="showPreview && selectedFile"
            :size="100 - previewHeight"
            :minSize="20"
          >
            <NxFilePreviewPane
              :selectedFile="selectedFile"
              @close="selectedFile = null"
              @file-action="handleFileAction"
              @file-renamed="handleFileRenamed"
            />
          </SplitterPanel>
        </Splitter>
      </SplitterPanel>
    </Splitter>
    </template>

    <template v-else>
      <div class="flex flex-column h-full">
        <!-- Simplified layout without fixed panes -->
      </div>
    </template>

    <!-- Mobile Layout -->
    <div v-else class="mobile-layout">
      <!-- Mobile Header -->
      <div class="mobile-header">
        <Button
          @click="showSidebar = !showSidebar"
          icon="pi pi-bars"
          size="small"
        />
        <h6>File Manager</h6>
        <Button
          v-if="selectedFile"
          @click="selectedFile = null"
          icon="pi pi-times"
          size="small"
        />
      </div>

      <!-- Mobile Sidebar (overlay) -->
      <div v-if="showSidebar" class="mobile-sidebar-overlay" @click="showSidebar = false">
        <div class="mobile-sidebar" @click.stop>
          <NxFileTree
            v-model:selectedCategories="selectedCategories"
            :categories="categories"
            :hierarchical="hierarchical"
            :showCounts="showCounts"
            :treeData="treeData"
            :allowCreate="allowCreateCategory"
            @category-select="handleCategorySelect"
            @category-created="handleCategoryCreated"
          />
        </div>
      </div>

      <!-- Mobile Content -->
      <div class="mobile-content">
        <NxFileListView
          :files="filteredFiles"
          :loading="loading"
          :viewMode="viewMode"
          :selectedFiles.sync="selectedFiles"
          :allowUpload="allowUpload"
          :allowCreateCategory="allowCreateCategory"
          @row-action="handleFileAction"
          @bulk-action="handleBulkAction"
          @upload="handleUpload"
          @create-category="handleCreateCategory"
          @file-select="handleFileSelect"
          @file-open="handleFileOpen"
        />

        <!-- Mobile Preview Modal -->
        <Dialog
          v-model:visible="showPreviewModal"
          modal
          :header="selectedFile?.title || selectedFile?.original_filename || 'File Preview'"
          :style="{ width: '90vw', maxWidth: '500px' }"
          :closable="true"
        >
          <NxFilePreviewPane
            v-if="selectedFile"
            :selectedFile="selectedFile"
            @file-action="handleFileAction"
            @file-renamed="handleFileRenamed"
          />
        </Dialog>
      </div>
    </div>


    <!-- Bulk Operations Dialog -->
    <Dialog
      v-model:visible="showBulkDialog"
      modal
      :header="bulkOperation + ' Files'"
      :style="{ width: '400px' }"
    >
      <div v-if="bulkOperation === 'copy' || bulkOperation === 'move'">
        <label>Select destination category:</label>
        <Dropdown
          v-model="targetCategoryId"
          :options="categories"
          optionLabel="name"
          optionValue="id"
          placeholder="Choose category"
          class="w-full mt-2"
        />
      </div>

      <div v-if="bulkOperation === 'delete'" class="delete-confirm">
        <p>Are you sure you want to delete {{ selectedFiles.length }} file{{ selectedFiles.length > 1 ? 's' : '' }}?</p>
        <small class="text-red-500">This action cannot be undone.</small>
      </div>

      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="showBulkDialog = false"
        />
        <Button
          :label="bulkOperation.charAt(0).toUpperCase() + bulkOperation.slice(1)"
          :icon="getBulkIcon(bulkOperation)"
          :loading="bulkProcessing"
          :severity="bulkOperation === 'delete' ? 'danger' : 'primary'"
          @click="executeBulkOperation"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, inject, defineProps, defineEmits } from 'vue'
import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import NxFileTree from './components/NxFileTree.vue'
import NxFileListView from './components/NxFileListView.vue'
import NxFilePreviewPane from './components/NxFilePreviewPane.vue'

// Props
const props = defineProps({
  // Display options
  showPreview: { type: Boolean, default: true },
  defaultViewMode: { type: String, default: 'list' }, // 'list' | 'grid'

  // Selection options
  selectionMode: { type: String, default: 'single' }, // 'single' | 'multiple'

  // Layout options
  sidebarWidth: { type: Number, default: 20 },
  previewHeight: { type: Number, default: 70 },
  useSplitter: { type: Boolean, default: true },

  // Integration options
  compact: { type: Boolean, default: false },
  height: { type: String, default: '100%' },
  showTree: { type: Boolean, default: true },
  showPreview: { type: Boolean, default: true },

  // Tree/Category options
  hierarchical: { type: Boolean, default: false }, // Enable hierarchical categories (future)
  showCounts: { type: Boolean, default: true }, // Show file counts in categories
  treeData: { type: Array, default: () => [] }, // Hierarchical tree data (future)

  // Feature flags
  allowUpload: { type: Boolean, default: true },
  allowCreateCategory: { type: Boolean, default: true },
  allowBulkOperations: { type: Boolean, default: true }
})

// Emits
const emit = defineEmits(['file-uploaded', 'file-deleted', 'file-copied', 'file-moved', 'category-created'])

// Services
const fileService = inject('files')
const categoryService = inject('file-categories')
const fileOperationsService = inject('fileOperations')

// Data
const categories = ref([])
const files = ref([])
const selectedCategories = ref([])
const selectedFiles = ref([])
const selectedFile = ref(null)

// UI State
const loading = ref(false)
const viewMode = ref(props.defaultViewMode)
const showSidebar = ref(false)
const showPreviewModal = ref(false)
const showBulkDialog = ref(false)

// Operations
const bulkOperation = ref('')
const targetCategoryId = ref(null)
const bulkProcessing = ref(false)

// Responsive
const windowWidth = ref(window.innerWidth)

// Computed
const isMobile = computed(() => windowWidth.value < 768)

const filteredFiles = computed(() => {
  if (selectedCategories.value.length === 0) {
    return files.value
  }
  return files.value.filter(file =>
    selectedCategories.value.includes(file.category_id)
  )
})

// Methods
const loadData = async () => {
  loading.value = true
  try {
    const categoriesResult = await categoryService.list({ paginated: false })
    categories.value = categoriesResult.data.data

    const filesResult = await fileService.list({ paginated: false })
    files.value = filesResult.data.data
  } catch (error) {
    console.error('Load data error:', error)
  } finally {
    loading.value = false
  }
}

const handleCategorySelect = (categoryId) => {
  if (props.selectionMode === 'single') {
    selectedCategories.value = [categoryId]
  } else {
    if (!selectedCategories.value.includes(categoryId)) {
      selectedCategories.value.push(categoryId)
    }
  }
}

const handleCategoryUnselect = (categoryId) => {
  selectedCategories.value = selectedCategories.value.filter(id => id !== categoryId)
}

const handleViewModeChange = (newViewMode) => {
  viewMode.value = newViewMode
}

const handleCategoryCreated = (category) => {
  categories.value.push(category)
  loadData() // Refresh to get updated data
}

const handleFileSelect = (file) => {
  selectedFile.value = file
  if (isMobile.value) {
    showPreviewModal.value = true
  }
}

const handleFileOpen = (file) => {
  if (file.storage_url) {
    window.open(file.storage_url, '_blank')
  }
}

const handleFileAction = (action, file) => {
  switch (action) {
    case 'view':
      handleFileSelect(file)
      break
    case 'edit':
      // Could open edit dialog
      break
    case 'delete':
      executeFileAction('delete', [file])
      break
    case 'copy':
      initiateBulkOperation('copy', [file])
      break
    case 'move':
      initiateBulkOperation('move', [file])
      break
  }
}

const handleBulkAction = ({ action, selectedFiles: files }) => {
  initiateBulkOperation(action, files)
}

const initiateBulkOperation = (action, files) => {
  bulkOperation.value = action
  selectedFiles.value = files
  showBulkDialog.value = true
}

const executeBulkOperation = async () => {
  if (!bulkOperation.value || selectedFiles.value.length === 0) return

  bulkProcessing.value = true
  try {
    let result

    switch (bulkOperation.value) {
      case 'copy':
        result = await fileOperationsService.copyFiles(
          selectedFiles.value.map(f => f.id),
          targetCategoryId.value
        )
        if (result.success) {
          emit('file-copied', result.results)
          loadData()
        }
        break

      case 'move':
        result = await fileOperationsService.moveFiles(
          selectedFiles.value.map(f => f.id),
          targetCategoryId.value
        )
        if (result.success) {
          emit('file-moved', result.results)
          loadData()
        }
        break

      case 'delete':
        await executeFileAction('delete', selectedFiles.value)
        break
    }

    showBulkDialog.value = false
    selectedFiles.value = []
    bulkOperation.value = ''
    targetCategoryId.value = null
  } catch (error) {
    console.error('Bulk operation error:', error)
  } finally {
    bulkProcessing.value = false
  }
}

const executeFileAction = async (action, files) => {
  try {
    for (const file of files) {
      switch (action) {
        case 'delete':
          await fileService.delete(file.id)
          emit('file-deleted', file)
          break
      }
    }
    loadData()
  } catch (error) {
    console.error('File action error:', error)
  }
}

const handleFileUploaded = (uploadedFile) => {
  // Add uploaded file to the list
  files.value.push(uploadedFile)
  emit('file-uploaded', uploadedFile)
}

const handleCreateCategory = () => {
  // This could emit an event or show a dialog
  emit('create-category-requested')
}

const handleFileRenamed = ({ fileId, newTitle }) => {
  const fileIndex = files.value.findIndex(f => f.id === fileId)
  if (fileIndex !== -1) {
    files.value[fileIndex].title = newTitle
  }
}

const handleResize = () => {
  windowWidth.value = window.innerWidth
}

const getBulkIcon = (operation) => {
  const icons = {
    copy: 'pi pi-copy',
    move: 'pi pi-arrow-right',
    delete: 'pi pi-trash'
  }
  return icons[operation] || 'pi pi-check'
}

// Lifecycle
onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>

.file-manager-splitter {
  height: 100%;
  border: 1px solid var(--surface-border);
}

.mobile-layout {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mobile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid var(--surface-border);
  background: var(--surface-section);
}

.mobile-header h6 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.mobile-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
}

.mobile-sidebar {
  width: 280px;
  height: 100%;
  background: var(--surface-card);
  border-right: 1px solid var(--surface-border);
}

.mobile-content {
  flex: 1;
  overflow: hidden;
}

.upload-progress {
  margin-top: 1rem;
}

.delete-confirm {
  text-align: center;
  padding: 1rem 0;
}

.delete-confirm p {
  margin-bottom: 0.5rem;
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .file-manager {
    height: 100vh;
  }
}
</style>
