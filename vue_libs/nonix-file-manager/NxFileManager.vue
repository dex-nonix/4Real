<template>
  <div class="file-manager" :class="{ 'mobile': isMobile }">
    <Splitter
      v-if="!isMobile"
      :gutterSize="8"
      class="file-manager-splitter"
    >
      <!-- Sidebar Tree -->
      <SplitterPanel :size="sidebarWidth" :minSize="20">
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

<script>
import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import NxFileTree from './components/NxFileTree.vue'
import NxFileListView from './components/NxFileListView.vue'
import NxFilePreviewPane from './components/NxFilePreviewPane.vue'
import { inject, ref, computed, onMounted } from 'vue'

export default {
  name: 'NxFileManager',
  components: {
    Splitter,
    SplitterPanel,
    Button,
    Dialog,
    Dropdown,
    NxFileTree,
    NxFileListView,
    NxFilePreviewPane
  },
  props: {
    // Display options
    showPreview: { type: Boolean, default: true },
    defaultViewMode: { type: String, default: 'list' }, // 'list' | 'grid'

    // Selection options
    selectionMode: { type: String, default: 'single' }, // 'single' | 'multiple'

    // Layout options
    sidebarWidth: { type: Number, default: 25 },
    previewHeight: { type: Number, default: 70 },

    // Tree/Category options
    hierarchical: { type: Boolean, default: false }, // Enable hierarchical categories (future)
    showCounts: { type: Boolean, default: true }, // Show file counts in categories
    treeData: { type: Array, default: () => [] }, // Hierarchical tree data (future)

    // Feature flags
    allowUpload: { type: Boolean, default: true },
    allowCreateCategory: { type: Boolean, default: true },
    allowBulkOperations: { type: Boolean, default: true }
  },
  emits: ['file-uploaded', 'file-deleted', 'file-copied', 'file-moved', 'category-created'],
  setup() {
    const fileService = inject('files')
    const categoryService = inject('file-categories')
    const fileOperationsService = inject('fileOperations')

    return {
      fileService,
      categoryService,
      fileOperationsService
    }
  },
  data() {
    return {
      // Data
      categories: [],
      files: [],
      selectedCategories: [],
      selectedFiles: [],
      selectedFile: null,

      // UI State
      loading: false,
      viewMode: this.defaultViewMode,
      showSidebar: false,
      showPreviewModal: false,
      showBulkDialog: false,

      // Operations
      bulkOperation: '',
      targetCategoryId: null,
      bulkProcessing: false,

      // Responsive
      windowWidth: window.innerWidth
    }
  },
  computed: {
    isMobile() {
      return this.windowWidth < 768
    },

    filteredFiles() {
      if (this.selectedCategories.length === 0) {
        return this.files
      }
      return this.files.filter(file =>
        this.selectedCategories.includes(file.category_id)
      )
    }
  },
  mounted() {
    this.loadData()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const categoriesResult = await this.categoryService.list({ paginated: false })
        this.categories = categoriesResult.data.data

        const filesResult = await this.fileService.list({ paginated: false })
        this.files = filesResult.data.data
      } catch (error) {
        console.error('Load data error:', error)
      } finally {
        this.loading = false
      }
    },

    handleCategorySelect(categoryId) {
      if (this.selectionMode === 'single') {
        this.selectedCategories = [categoryId]
      } else {
        if (!this.selectedCategories.includes(categoryId)) {
          this.selectedCategories.push(categoryId)
        }
      }
    },

    handleCategoryUnselect(categoryId) {
      this.selectedCategories = this.selectedCategories.filter(id => id !== categoryId)
    },

    handleViewModeChange(newViewMode) {
      this.viewMode = newViewMode
    },

    handleCategoryCreated(category) {
      this.categories.push(category)
      this.loadData() // Refresh to get updated data
    },

    handleFileSelect(file) {
      this.selectedFile = file
      if (this.isMobile) {
        this.showPreviewModal = true
      }
    },

    handleFileAction(action, file) {
      switch (action) {
        case 'view':
          this.handleFileSelect(file)
          break
        case 'edit':
          // Could open edit dialog
          break
        case 'delete':
          this.executeFileAction('delete', [file])
          break
        case 'copy':
          this.initiateBulkOperation('copy', [file])
          break
        case 'move':
          this.initiateBulkOperation('move', [file])
          break
      }
    },

    handleBulkAction({ action, selectedFiles }) {
      this.initiateBulkOperation(action, selectedFiles)
    },

    initiateBulkOperation(action, files) {
      this.bulkOperation = action
      this.selectedFiles = files
      this.showBulkDialog = true
    },

    async executeBulkOperation() {
      if (!this.bulkOperation || this.selectedFiles.length === 0) return

      this.bulkProcessing = true
      try {
        let result

        switch (this.bulkOperation) {
          case 'copy':
            result = await this.fileOperationsService.copyFiles(
              this.selectedFiles.map(f => f.id),
              this.targetCategoryId
            )
            if (result.success) {
              this.$emit('file-copied', result.results)
              this.loadData()
            }
            break

          case 'move':
            result = await this.fileOperationsService.moveFiles(
              this.selectedFiles.map(f => f.id),
              this.targetCategoryId
            )
            if (result.success) {
              this.$emit('file-moved', result.results)
              this.loadData()
            }
            break

          case 'delete':
            await this.executeFileAction('delete', this.selectedFiles)
            break
        }

        this.showBulkDialog = false
        this.selectedFiles = []
        this.bulkOperation = ''
        this.targetCategoryId = null
      } catch (error) {
        console.error('Bulk operation error:', error)
      } finally {
        this.bulkProcessing = false
      }
    },

    async executeFileAction(action, files) {
      try {
        for (const file of files) {
          switch (action) {
            case 'delete':
              await this.fileService.delete(file.id)
              this.$emit('file-deleted', file)
              break
          }
        }
        this.loadData()
      } catch (error) {
        console.error('File action error:', error)
      }
    },


    handleFileUploaded(uploadedFile) {
      // Add uploaded file to the list
      this.files.push(uploadedFile)
      this.$emit('file-uploaded', uploadedFile)
    },

    handleCreateCategory() {
      // This could emit an event or show a dialog
      this.$emit('create-category-requested')
    },



    handleFileRenamed({ fileId, newTitle }) {
      const fileIndex = this.files.findIndex(f => f.id === fileId)
      if (fileIndex !== -1) {
        this.files[fileIndex].title = newTitle
      }
    },

    handleResize() {
      this.windowWidth = window.innerWidth
    },

    getBulkIcon(operation) {
      const icons = {
        copy: 'pi pi-copy',
        move: 'pi pi-arrow-right',
        delete: 'pi pi-trash'
      }
      return icons[operation] || 'pi pi-check'
    }
  }
}
</script>

<style scoped>
.file-manager {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

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
