# **PERFECT NxFileView File Actions - Enhanced Service Solution**

## **Overview**
Implement individual file action dialogs in `NxFileView.vue` with **enhanced NxFileManagerService** that emits events automatically. No props/events passing through component hierarchy. Fix download functionality.

## **Core Concept**
**NxFileManagerService** becomes the single source of truth - handles operations AND emits events. Components inject the service and listen to its events. Clean, no "creepy" prop passing.

## **Files to Modify**

### **1. NxFileManagerService.js - ENHANCE EXISTING SERVICE**

#### **Add EventEmitter & Subscription Methods**
```javascript
import NxBaseApiService from '@nonix-api/services/NxBaseApiService.js'
import { EventEmitter } from 'events'

export default class NxFileManagerService extends NxBaseApiService {
  constructor(app) {
    super(app)
    this.basePath = () => '/file-manager'
    this.events = new EventEmitter()  // ADD THIS
  }

  // ADD: Event subscription methods
  onFileRenamed(callback) {
    this.events.on('file-renamed', callback)
    return () => this.events.off('file-renamed', callback)
  }

  onFileCopied(callback) {
    this.events.on('file-copied', callback)
    return () => this.events.off('file-copied', callback)
  }

  onFileMoved(callback) {
    this.events.on('file-moved', callback)
    return () => this.events.off('file-moved', callback)
  }

  onFileDeleted(callback) {
    this.events.on('file-deleted', callback)
    return () => this.events.off('file-deleted', callback)
  }
```

#### **Enhance Operation Methods to Emit Events**
```javascript
// ENHANCE: Existing methods to emit events after success
async bulkCopyFiles(fileIds, targetCategoryId) {
  const result = await this.post('/bulk/copy', { fileIds, targetCategoryId })
  if (result.success && result.results) {
    result.results.forEach(file => this.events.emit('file-copied', file))  // ADD
  }
  return result
}

async bulkMoveFiles(fileIds, targetCategoryId) {
  const result = await this.post('/bulk/move', { fileIds, targetCategoryId })
  if (result.success && result.results) {
    result.results.forEach(file => this.events.emit('file-moved', file))  // ADD
  }
  return result
}

async bulkDeleteFiles(fileIds) {
  // Get files before deletion for event emission
  const filesToDelete = await this.getFilesByIds(fileIds)  // ADD HELPER
  const result = await this.post('/bulk/delete', { fileIds })
  if (result.success) {
    filesToDelete.forEach(file => this.events.emit('file-deleted', file))  // ADD
  }
  return result
}

async renameFile(fileId, newTitle) {
  const result = await this.put(`/files/${fileId}/rename`, { newTitle })
  if (result.success) {
    this.events.emit('file-renamed', { fileId, newTitle })  // ADD
  }
  return result
}

// ADD: Helper method for delete events
async getFilesByIds(fileIds) {
  const allFiles = await this.listFiles()
  return allFiles.data.data.filter(file => fileIds.includes(file.id))
}
```

### **2. NxFileView.vue - CLEAN IMPLEMENTATION**

#### **Add Imports**
```javascript
// Add to existing imports
import Dropdown from 'primevue/dropdown'
import { downloadFile } from '../utils/index.js'
```

#### **Update Props - MINIMAL**
```javascript
const props = defineProps({
  selectedFile: { type: Object, required: true },
  maximizeMode: {
    type: String,
    default: 'dialog',
    validator: value => ['dialog', 'fullscreen'].includes(value)
  },
  // NEW: Only what we need
  categories: { type: Array, default: () => [] },
  fileManagerService: { type: Object, required: true }  // Already injected in parent
})
```

#### **Update Emits - MINIMAL**
```javascript
const emit = defineEmits([
  'open-fullscreen-dialog'  // Only fullscreen, no file operation events!
])
```

#### **Add Reactive State**
```javascript
// Existing state
const showRenameDialog = ref(false)
const newTitle = ref('')
const renaming = ref(false)
const isFullscreen = ref(false)

// NEW STATE FOR FILE ACTIONS
const showCopyDialog = ref(false)
const showMoveDialog = ref(false)
const showDeleteDialog = ref(false)
const targetCategoryId = ref(null)
const copying = ref(false)
const moving = ref(false)
const deleting = ref(false)
```

#### **Update Template - Add Dialogs**
```vue
<!-- Copy File Dialog -->
<Dialog v-model:visible="showCopyDialog" modal header="Copy File" :style="{ width: '400px' }">
  <div class="p-fluid">
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
  <template #footer>
    <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="showCopyDialog = false" />
    <Button label="Copy" icon="pi pi-copy" :loading="copying" @click="executeCopy" />
  </template>
</Dialog>

<!-- Move File Dialog -->
<Dialog v-model:visible="showMoveDialog" modal header="Move File" :style="{ width: '400px' }">
  <div class="p-fluid">
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
  <template #footer>
    <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="showMoveDialog = false" />
    <Button label="Move" icon="pi pi-arrow-right" :loading="moving" @click="executeMove" />
  </template>
</Dialog>

<!-- Delete File Dialog -->
<Dialog v-model:visible="showDeleteDialog" modal header="Delete File" :style="{ width: '400px' }">
  <div class="delete-confirm">
    <p>Are you sure you want to delete this file?</p>
    <small class="text-red-500">This action cannot be undone.</small>
  </div>
  <template #footer>
    <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="showDeleteDialog = false" />
    <Button label="Delete" icon="pi pi-trash" severity="danger" :loading="deleting" @click="executeDelete" />
  </template>
</Dialog>
```

#### **Update Action Buttons**
```vue
<div class="flex flex-wrap gap-2 mt-3 flex-shrink-0">
  <Button
    v-if="hasPreviewUrl"
    icon="pi pi-download"
    text rounded v-tooltip.top="'Download'"
    size="small"
    @click="downloadFile(selectedFile)"  <!-- FIXED -->
  />
  <Button icon="pi pi-pencil" text rounded v-tooltip.top="'Rename'" size="small" @click="showRenameDialog = true" />
  <Button icon="pi pi-copy" text rounded v-tooltip.top="'Copy'" size="small" @click="openCopyDialog" />
  <Button icon="pi pi-arrow-right" text rounded v-tooltip.top="'Move'" size="small" @click="openMoveDialog" />
  <Button icon="pi pi-trash" text rounded v-tooltip.top="'Delete'" size="small" severity="danger" @click="openDeleteDialog" />
</div>
```

#### **Add Execute Methods - CLEAN**
```javascript
const openCopyDialog = () => { targetCategoryId.value = null; showCopyDialog.value = true }
const openMoveDialog = () => { targetCategoryId.value = null; showMoveDialog.value = true }
const openDeleteDialog = () => { showDeleteDialog.value = true }

const executeCopy = async () => {
  if (!targetCategoryId.value) return
  copying.value = true
  try {
    await fileManagerService.bulkCopyFiles([selectedFile.value.id], targetCategoryId.value)
    showCopyDialog.value = false  // Service emits event automatically!
  } catch (error) {
    console.error('Copy error:', error)
  } finally {
    copying.value = false
  }
}

const executeMove = async () => {
  if (!targetCategoryId.value) return
  moving.value = true
  try {
    await fileManagerService.bulkMoveFiles([selectedFile.value.id], targetCategoryId.value)
    showMoveDialog.value = false  // Service emits event automatically!
  } catch (error) {
    console.error('Move error:', error)
  } finally {
    moving.value = false
  }
}

const executeDelete = async () => {
  deleting.value = true
  try {
    await fileManagerService.bulkDeleteFiles([selectedFile.value.id])
    showDeleteDialog.value = false  // Service emits event automatically!
  } catch (error) {
    console.error('Delete error:', error)
  } finally {
    deleting.value = false
  }
}
```

### **3. NxFileManager.vue - Listen to Service Events**

#### **Subscribe to Service Events in onMounted**
```javascript
// Already injected
const fileManagerService = inject('file-manager')

onMounted(async () => {
  loadData()
  window.addEventListener('resize', handleResize)

  // CRITICAL: Subscribe to service events - NO PROPS/EVENTS FROM CHILD COMPONENTS!
  const unsubscribeRenamed = fileManagerService.onFileRenamed(handleFileRenamed)
  const unsubscribeCopied = fileManagerService.onFileCopied(handleFileCopied)
  const unsubscribeMoved = fileManagerService.onFileMoved(handleFileMoved)
  const unsubscribeDeleted = fileManagerService.onFileDeleted(handleFileDeleted)

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    unsubscribeRenamed()
    unsubscribeCopied()
    unsubscribeMoved()
    unsubscribeDeleted()
  })
})
```

#### **Event Handlers - Update Local State**
```javascript
const handleFileRenamed = ({ fileId, newTitle }) => {
  const fileIndex = files.value.findIndex(f => f.id === fileId)
  if (fileIndex !== -1) {
    files.value[fileIndex].title = newTitle
  }
}

const handleFileCopied = (file) => {
  files.value.push(file)
  updateCategoryCount(file.category_id, 1)
}

const handleFileMoved = (file) => {
  const index = files.value.findIndex(f => f.id === file.id)
  if (index !== -1) {
    const oldCategoryId = files.value[index].category_id
    files.value[index] = file
    updateCategoryCount(oldCategoryId, -1)
    updateCategoryCount(file.category_id, 1)
  }
}

const handleFileDeleted = (file) => {
  const index = files.value.findIndex(f => f.id === file.id)
  if (index !== -1) {
    files.value.splice(index, 1)
    updateCategoryCount(file.category_id, -1)
  }
}
```

#### **Clean Component Usage - NO FILE OPERATION EVENTS**
```vue
<!-- Mobile Preview -->
<NxFilePreviewPane
  :selectedFile="selectedFile"
  :categories="categories"
  :fileManagerService="fileManagerService"
  @close="showPreviewModal = false"
  @open-fullscreen-dialog="openFullscreenView(selectedFile)"
/>

<!-- Fullscreen Dialog -->
<NxFileViewDialog
  v-model:visible="showFullscreenView"
  :selectedFile="fullscreenViewFile"
  :categories="categories"
  :fileManagerService="fileManagerService"
/>
```

### **4. NxFilePreviewPane.vue & NxFileViewDialog.vue - MINIMAL PASSTHROUGH**

#### **NxFilePreviewPane.vue**
```vue
<template>
  <!-- ... existing template ... -->
  <NxFileView
    :selectedFile="selectedFile"
    :maximizeMode="'dialog'"
    :categories="categories"
    :fileManagerService="fileManagerService"
    @open-fullscreen-dialog="$emit('open-fullscreen-dialog')"
  />
</template>

<script setup>
// Only pass through props, no file operation event handling!
const props = defineProps({
  selectedFile: { type: Object, default: null },
  useCard: { type: Boolean, default: false },
  categories: { type: Array, default: () => [] },
  fileManagerService: { type: Object, required: true }
})

const emit = defineEmits(['close', 'open-fullscreen-dialog'])  // No file operation events!
</script>
```

#### **NxFileViewDialog.vue**
```vue
<template>
  <Dialog v-model:visible="visible" modal :header="selectedFile?.title || selectedFile?.original_filename || 'File View'" :style="dialogStyle">
    <NxFileView
      :selectedFile="selectedFile"
      :maximizeMode="'fullscreen'"
      :categories="categories"
      :fileManagerService="fileManagerService"
    />
    <!-- ... footer ... -->
  </Dialog>
</template>

<script setup>
// Only pass through props, no file operation event handling!
const props = defineProps({
  visible: { type: Boolean, default: false },
  selectedFile: { type: Object, default: null },
  categories: { type: Array, default: () => [] },
  fileManagerService: { type: Object, required: true }
})

const emit = defineEmits(['update:visible'])  // No file operation events!
</script>
```

## **PERFECT Event Flow**

### **✅ Copy/Move/Delete Flow** (Service-Driven)
1. `NxFileView` calls `fileManagerService.bulkCopyFiles()`
2. Service executes operation + emits `'file-copied'` event automatically
3. `NxFileManager` listens to service event → updates local state
4. UI reacts automatically (Vue reactivity)

### **✅ Rename Flow** (Service-Driven)
1. `NxFileView` calls `fileManagerService.renameFile()`
2. Service executes operation + emits `'file-renamed'` event automatically
3. `NxFileManager` listens to service event → updates local state
4. UI reacts automatically

### **✅ Download Flow** (Direct)
1. `NxFileView` calls `downloadFile(selectedFile)` directly
2. No state changes needed

## **Implementation Steps**

1. **NxFileManagerService.js**: Add EventEmitter + enhance methods to emit events
2. **NxFileView.vue**: Add dialogs + execute methods (service emits events automatically)
3. **NxFileManager.vue**: Subscribe to service events + update local state
4. **NxFilePreviewPane.vue & NxFileViewDialog.vue**: Just pass through props

## **Why This is PERFECT**

✅ **Zero Props/Events Passing**: No "creepy" event bubbling through components  
✅ **Single Source of Truth**: Service handles operations AND events  
✅ **Already Injected**: No new dependencies  
✅ **Clean Components**: NxFileView just calls service methods  
✅ **Automatic Synchronization**: File manager updates when service emits events  
✅ **Reactive UI**: Vue handles all UI updates automatically  

## **Testing Checklist**

- [ ] Download works (`downloadFile(selectedFile)`)
- [ ] Copy dialog → calls service → service emits → file manager updates
- [ ] Move dialog → calls service → service emits → file manager updates  
- [ ] Delete dialog → calls service → service emits → file manager updates
- [ ] Category counts update correctly
- [ ] No duplicate files after copy
- [ ] UI updates immediately after operations
- [ ] No prop/event passing between components

## **Notes**

- **Service is KING**: Operations + Events in one place
- **Components are DUMB**: Just call service methods
- **File Manager is SMART**: Listens to service events
- **Zero Coupling**: Components don't know about each other's file operations
- **Future-Proof**: Any component can listen to service events
