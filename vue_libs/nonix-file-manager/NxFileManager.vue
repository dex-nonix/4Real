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
          ref="fileTreeRef"
          v-model:selectedCategories="selectedCategories"
          :categories="categories"
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
              :selectedFiles.sync="selectedFiles"
              :selectedCategories="selectedCategories"
              :categories="categories"
              :isMobile="isMobile"
              :allowUpload="allowUpload"
              @row-action="handleFileAction"
              @bulk-action="handleBulkAction"
              @view-mode-change="handleViewModeChange"
              @category-select="handleCategorySelectFromList"
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

    <!-- Mobile Layout -->
    <div v-else class="mobile-layout">
      <!-- Mobile Content -->
      <div class="mobile-content">
        <NxFileListView
          :files="filteredFiles"
          :loading="loading"
          :viewMode="viewMode"
          :selectedFiles.sync="selectedFiles"
          :categories="categories"
          :isMobile="isMobile"
          :allowUpload="allowUpload"
          :allowCreateCategory="allowCreateCategory"
          @row-action="handleFileAction"
          @bulk-action="handleBulkAction"
          @view-mode-change="handleViewModeChange"
          @create-category="handleCreateCategory"
          @category-select="handleCategorySelectFromList"
          @file-select="handleFileSelect"
          @file-open="handleFileOpen"
          @file-uploaded="handleFileUploaded"
        />

        <!-- Remove the unused @upload="handleUpload" -->

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
    </template>

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
import { downloadFile } from './utils/index.js'

// Props
const props = defineProps({
  // Display options
  showPreview: { type: Boolean, default: true },
  defaultViewMode: { type: String, default: 'list' }, // 'list' | 'grid'


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
const fileManagerService = inject('file-manager')

// Data
const categories = ref([])
const files = ref([])
const selectedCategories = ref([])
const selectedFiles = ref([])
const selectedFile = ref(null)

// Component refs
const fileTreeRef = ref(null)

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
    const categoriesResult = await fileManagerService.getCategoriesWithCounts()
    categories.value = categoriesResult.data.data

    const filesResult = await fileManagerService.listFiles()
    files.value = filesResult.data.data
  } catch (error) {
    console.error('Load data error:', error)
  } finally {
    loading.value = false
  }
}

const updateCategoryCount = (categoryId, delta) => {
  const category = categories.value.find(c => c.id === categoryId)
  if (category) {
    category.file_count = (category.file_count || 0) + delta
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

const handleCategorySelectFromList = (categoryId) => {
  if (categoryId === null) {
    selectedCategories.value = []
  } else {
    selectedCategories.value = [categoryId]
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
}

const handleFileSelect = (file) => {
  selectedFile.value = file
  if (isMobile.value) {
    showPreviewModal.value = true
  }
}

const handleFileOpen = (file) => {
  downloadFile(file)
}

const deleteFile = (file) => {
  selectedFiles.value = [file]
  bulkOperation.value = 'delete'
  showBulkDialog.value = true
}

const handleFileAction = ({ action, file }) => {
  switch (action) {
    case 'view':
      handleFileSelect(file)
      break
    case 'edit':
      // Could open edit dialog
      break
    case 'delete':
      deleteFile(file)
      break
    case 'copy':
      selectedFiles.value = [file]
      bulkOperation.value = 'copy'
      showBulkDialog.value = true
      break
    case 'move':
      selectedFiles.value = [file]
      bulkOperation.value = 'move'
      showBulkDialog.value = true
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
        result = await fileManagerService.bulkCopyFiles(
          selectedFiles.value.map(f => f.id),
          targetCategoryId.value
        )
        if (result.success) {
          emit('file-copied', result.results)
          // Add copied files to the list
          files.value.push(...result.results)
        }
        break

      case 'move':
        // Get source categories before move
        const sourceCategories = [...new Set(selectedFiles.value.map(f => f.category_id))]

        result = await fileManagerService.bulkMoveFiles(
          selectedFiles.value.map(f => f.id),
          targetCategoryId.value
        )
        if (result.success) {
          emit('file-moved', result.results)
          // Update file list with moved files
          for (const movedFile of result.results) {
            const index = files.value.findIndex(f => f.id === movedFile.id)
            if (index !== -1) {
              files.value[index] = movedFile
            }
          }
        }
        break

      case 'delete':
        const fileIds = selectedFiles.value.map(f => f.id)
        await fileManagerService.bulkDeleteFiles(fileIds)
        // Remove from local file list
        for (const file of selectedFiles.value) {
          const index = files.value.findIndex(f => f.id === file.id)
          if (index !== -1) {
            files.value.splice(index, 1)
          }
          updateCategoryCount(file.category_id, -1)
        }
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


const handleFileUploaded = (uploadedFile) => {
  // Add uploaded file to the list
  files.value.push(uploadedFile)
  emit('file-uploaded', uploadedFile)

  // Update count for the category
  updateCategoryCount(uploadedFile.category_id, 1)
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
