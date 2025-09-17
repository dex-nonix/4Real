# File Manager Component Integration Plan

## Overview

Build a standalone `NxFileManager.vue` component that provides a complete file management experience using existing services. The component should be mobile-first, include tree navigation, multi-select operations, and preview functionality.

## Current Architecture Analysis

### ✅ Available Services & Components

- **NxFileService** - Full CRUD + upload with progress tracking
- **NxFileCategoryService** - Category management (flat structure)
- **NxFileTypeManager** - Comprehensive file type detection & icons
- **NxFilePreview** - File preview component with type-aware rendering
- **NxDynamicTable** - Responsive table system with multi-select
- **PrimeVue Tree** - Available for hierarchical navigation

### ❌ Missing Components

1. **NxFileManager.vue** - Main container component
2. **NxFileTree.vue** - Tree navigation component
3. **NxFileListView.vue** - Enhanced file list with grid/thumbnail options
4. **NxFilePreviewPane.vue** - Full preview pane component
5. **NxFileOperations.vue** - File operation dialogs (copy, move, rename)

## Component Architecture

### NxFileManager.vue (Main Component)

```vue
<template>
  <div class="file-manager">
    <Splitter :gutterSize="8" class="file-manager-splitter">
      <!-- Sidebar Tree -->
      <SplitterPanel :size="25" :minSize="20">
        <NxFileTree
          v-model:selectedCategories="selectedCategories"
          :categories="categories"
          :hierarchical="hierarchical"
          :showCounts="showCounts"
          :treeData="treeData"
          @category-select="handleCategorySelect"
        />
      </SplitterPanel>

      <!-- Main Content Area -->
      <SplitterPanel :size="75" :minSize="50">
        <Splitter orientation="vertical">
          <!-- File List -->
          <SplitterPanel :size="70" :minSize="40">
            <NxFileListView
              :files="filteredFiles"
              :loading="loading"
              :viewMode="viewMode"
              :selectedFiles="selectedFiles"
              @file-select="handleFileSelect"
              @file-action="handleFileAction"
              @bulk-action="handleBulkAction"
            />
          </SplitterPanel>

          <!-- Preview Pane -->
          <SplitterPanel :size="30" :minSize="20" v-if="showPreview">
            <NxFilePreviewPane
              :selectedFile="selectedFile"
              @close="showPreview = false"
            />
          </SplitterPanel>
        </Splitter>
      </SplitterPanel>
    </Splitter>
  </div>
</template>
```

### NxFileTree.vue (Tree Navigation)

```vue
<template>
  <div class="file-tree">
    <!-- Flat Categories View (initial implementation) -->
    <div v-if="!hierarchical" class="flat-categories">
      <div
        v-for="category in categories"
        :key="category.id"
        :class="['category-item', { 'selected': selectedCategories.includes(category.id) }]"
        @click="toggleCategory(category.id)"
      >
        <i :class="getCategoryIcon(category)" class="mr-2"></i>
        <span>{{ category.name }}</span>
        <small v-if="showCounts" class="ml-auto text-muted">
          {{ getCategoryFileCount(category.id) }}
        </small>
      </div>
    </div>

    <!-- Hierarchical Tree View (future implementation) -->
    <Tree
      v-else
      :value="treeData"
      selectionMode="multiple"
      v-model:selectionKeys="selectedKeys"
      @node-select="handleNodeSelect"
      @node-unselect="handleNodeUnselect"
    >
      <template #default="slotProps">
        <span class="tree-node">
          <i :class="getCategoryIcon(slotProps.node)" class="mr-2"></i>
          {{ slotProps.node.label }}
          <small v-if="showCounts" class="ml-auto text-muted">
            {{ slotProps.node.fileCount || 0 }}
          </small>
        </span>
      </template>
    </Tree>
  </div>
</template>
```

```javascript
// NxFileTree Props
props: {
  categories: {
    type: Array,
    required: true
  },
  selectedCategories: {
    type: Array,
    default: () => []
  },
  hierarchical: {
    type: Boolean,
    default: false // Start with flat categories, set to true when parent_id is implemented
  },
  showCounts: {
    type: Boolean,
    default: true // Show file count per category
  },
  treeData: {
    type: Array,
    default: () => [] // For hierarchical tree structure (future use)
  }
},

// NxFileTree Emits
emits: ['category-select', 'category-unselect', 'selection-change']
```

### NxFileListView.vue (File Listing)

```vue
<template>
  <div class="file-list-view">
    <!-- Toolbar -->
    <div class="flex justify-between items-center p-3 border-bottom">
      <div class="flex gap-2">
        <Button @click="viewMode = 'list'" :outlined="viewMode !== 'list'">
          <i class="pi pi-list"></i>
        </Button>
        <Button @click="viewMode = 'grid'" :outlined="viewMode !== 'grid'">
          <i class="pi pi-th"></i>
        </Button>
      </div>
      <div class="flex gap-2">
        <Button @click="uploadFiles" icon="pi pi-upload" />
        <Button @click="createFolder" icon="pi pi-folder" />
      </div>
    </div>

    <!-- File List/Grid -->
    <div v-if="viewMode === 'list'" class="file-list">
      <NxDynamicTable
        :config="listConfig"
        :data="files"
        :loading="loading"
        :compact="true"
        selectionMode="multiple"
        v-model:selection="selectedFiles"
        @row-action="handleRowAction"
        @bulk-action="handleBulkAction"
      />
    </div>

    <div v-else class="file-grid">
      <DataView
        :value="files"
        :layout="viewMode"
        :loading="loading"
        selectionMode="multiple"
        v-model:selection="selectedFiles"
      >
        <template #grid="slotProps">
          <div class="file-grid-item" @click="selectFile(slotProps.data)">
            <NxFilePreview
              :value="slotProps.data"
              :showSize="true"
              :showCategory="true"
            />
          </div>
        </template>
      </DataView>
    </div>
  </div>
</template>
```

## Service Integration

### File Operations Service

```javascript
// NxFileOperationsService.js
export default class NxFileOperationsService {
  constructor(fileService, categoryService) {
    this.fileService = fileService
    this.categoryService = categoryService
  }

  async copyFiles(fileIds, targetCategoryId) {
    // Implementation
  }

  async moveFiles(fileIds, targetCategoryId) {
    // Implementation
  }

  async renameFile(fileId, newTitle) {
    // Implementation
  }

  async createCategory(name, parentId = null) {
    // Implementation
  }
}
```

## Configuration & Props

### NxFileManager Props

```javascript
props: {
  // Display options
  showPreview: { type: Boolean, default: true },
  defaultViewMode: { type: String, default: 'list' }, // 'list' | 'grid'

  // Selection options
  selectionMode: { type: String, default: 'multiple' }, // 'single' | 'multiple'

  // Layout options
  sidebarWidth: { type: Number, default: 25 },
  previewHeight: { type: Number, default: 30 },

  // Tree/Category options
  hierarchical: { type: Boolean, default: false }, // Enable hierarchical categories (future)
  showCounts: { type: Boolean, default: true }, // Show file counts in categories
  treeData: { type: Array, default: () => [] }, // Hierarchical tree data (future)

  // Feature flags
  allowUpload: { type: Boolean, default: true },
  allowCreateCategory: { type: Boolean, default: true },
  allowBulkOperations: { type: Boolean, default: true }
}
```

## Mobile Responsiveness

### Breakpoint Handling

- **Desktop (lg+)**: Full split-pane layout with tree, list, and preview
- **Tablet (md)**: Collapsible sidebar, stacked list/preview
- **Mobile (sm)**: Full-screen list, modal preview, drawer tree

### Touch Gestures

- Swipe to open/close sidebar
- Long press for multi-select
- Drag & drop for file operations (where supported)

## Events & Communication

### Emitted Events

```javascript
// File selection
'file-select' // { file, selectedFiles }

// File operations
'file-upload' // { files, categoryId }
'file-delete' // { fileIds }
'file-move' // { fileIds, targetCategoryId }
'file-copy' // { fileIds, targetCategoryId }

// Category operations
'category-create' // { name, parentId }
'category-rename' // { categoryId, newName }
'category-delete' // { categoryId }
```

## Integration Points

### 1. Service Registration

Add to `appConfig.js`:

```javascript
import NxFileOperationsService from '@nonix-file-manager/services/NxFileOperationsService.js'

service: {
  // ... existing services
  "fileOperations": (app) => new NxFileOperationsService(
    app._context.provides.files,
    app._context.provides['file-categories']
  )
}
```

### 2. Route Configuration

```javascript
routes: [
  // ... existing routes
  { path: '/file-manager', component: NxFileManager, meta: { layout: 'advanced' } }
]
```

### 3. Component Registration

```javascript
// In main app or plugin
import NxFileManager from '@nonix-file-manager/NxFileManager.vue'
import NxFileTree from '@nonix-file-manager/NxFileTree.vue'
import NxFileListView from '@nonix-file-manager/NxFileListView.vue'
import NxFilePreviewPane from '@nonix-file-manager/NxFilePreviewPane.vue'
```

## Implementation Priority

### Phase 1: Core Structure

1. Create `NxFileManager.vue` with basic split-pane layout
2. Implement `NxFileTree.vue` using existing categories
3. Create `NxFileListView.vue` extending dynamic table

### Phase 2: Enhanced Features

1. Add `NxFilePreviewPane.vue` component
2. Implement file operations service
3. Add grid view mode

### Phase 3: Advanced Features

1. Mobile responsiveness improvements
2. Drag & drop operations
3. Bulk operations UI
4. Search and filtering enhancements

## Dependencies

### PrimeVue Components Required

- `Splitter` & `SplitterPanel` - Layout management
- `Tree` - Hierarchical navigation
- `DataView` - Grid/list view switching
- `ContextMenu` - Right-click operations
- `Dialog` - Operation confirmations
- `Toast` - User feedback

### Existing Dependencies

- All existing file services
- `NxDynamicTable` for list view
- `NxFilePreview` for item rendering
- `NxFileTypeManager` for type detection

## Testing Strategy

### Unit Tests

- File operation services
- Component prop validation
- Event emission testing

### Integration Tests

- File upload flow
- Tree navigation
- Multi-select operations
- Mobile responsiveness

### E2E Tests

- Complete file management workflows
- Cross-device compatibility

## Performance Considerations

### Virtual Scrolling

- Implement virtual scrolling for large file lists
- Tree virtualization for deep category hierarchies

### Lazy Loading

- Load file previews on demand
- Paginate large category contents

### Caching

- Cache file type information
- Cache category tree structure

## Future Extensions

### Potential Enhancements

1. **Hierarchical Categories** - Add parent_id to FileCategory model and enable hierarchical tree navigation
2. **Cloud Storage Integration** - Add cloud provider connectors
3. **Advanced Search** - Full-text search with filters
4. **Version Control** - File versioning system
5. **Sharing** - File sharing and permissions
6. **Offline Support** - Service worker caching

This integration plan leverages 100% of existing services and components while providing a complete file management experience. The modular architecture allows for incremental implementation and easy testing.
