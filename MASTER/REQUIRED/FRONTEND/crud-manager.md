# 🎯 CrudManager Component

## 🎯 **PURPOSE:**
**Main CRUD component that combines DynamicForm and DynamicTable to provide complete CRUD functionality for any entity**

## 🏗️ **ARCHITECTURE:**

### **Core Concept:**
- **Orchestrates standalone components** - uses DynamicForm + DynamicTable
- **Configuration-driven** - different behavior per entity via config
- **Complete CRUD operations** - create, read, update, delete
- **Modal-based editing** - inline form editing with dialogs

## 🔧 **IMPLEMENTATION:**

### **1. CrudManager.vue Component:**
```vue
<template>
  <div class="crud-manager">
    <!-- Header with Actions -->
    <div class="crud-header flex justify-content-between align-items-center mb-4">
      <h1>{{ config.title || `${config.entity} Management` }}</h1>
      
      <div class="header-actions flex gap-3">
        <Button 
          @click="showCreateForm = true" 
          icon="pi pi-plus"
          label="Add New"
        />
        
        <Button 
          v-if="config.exportEnabled"
          @click="exportData" 
          icon="pi pi-download"
          severity="secondary"
          label="Export"
        />
      </div>
    </div>
    
    <!-- Data Table -->
    <DynamicTable
      :config="config.table"
      :data="entities"
      :loading="loading"
      @row-action="handleRowAction"
      @bulk-action="handleBulkAction"
    />
    
    <!-- Create/Edit Dialog -->
    <Dialog 
      v-model:visible="showCreateForm" 
      :header="dialogTitle"
      :modal="true"
      :closable="true"
      :close-on-escape="true"
      :style="{ width: '50vw' }"
    >
      <DynamicForm
        :config="config.form"
        :initial-data="editingEntity"
        :submit-label="isEditing ? 'Update' : 'Create'"
        @submit="handleFormSubmit"
        @cancel="closeDialog"
      />
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteConfirm" 
      header="Confirm Delete"
      :modal="true"
      :closable="true"
      :style="{ width: '30vw' }"
    >
      <div class="delete-confirmation">
        <p>Are you sure you want to delete this {{ config.entity }}?</p>
        <p class="entity-name">{{ entityToDelete?.name || entityToDelete?.title }}</p>
      </div>
      
      <template #footer>
        <Button 
          @click="showDeleteConfirm = false" 
          label="Cancel" 
          severity="secondary"
        />
        <Button 
          @click="confirmDelete" 
          label="Delete" 
          severity="danger"
          :loading="deleting"
        />
      </template>
    </Dialog>
    
    <!-- Bulk Delete Confirmation -->
    <Dialog 
      v-model:visible="showBulkDeleteConfirm" 
      header="Confirm Bulk Delete"
      :modal="true"
      :closable="true"
      :style="{ width: '30vw' }"
    >
      <div class="bulk-delete-confirmation">
        <p>Are you sure you want to delete {{ selectedEntities.length }} {{ config.entity }}s?</p>
        <p class="warning">This action cannot be undone.</p>
      </div>
      
      <template #footer>
        <Button 
          @click="showBulkDeleteConfirm = false" 
          label="Cancel" 
          severity="secondary"
        />
        <Button 
          @click="confirmBulkDelete" 
          label="Delete All" 
          severity="danger"
          :loading="bulkDeleting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { Dialog } from 'primevue/dialog'
import { Button } from 'primevue/button'
import DynamicTable from '@/components/tables/DynamicTable.vue'
import DynamicForm from '@/components/forms/DynamicForm.vue'

export default {
  name: 'CrudManager',
  components: { Dialog, Button, DynamicTable, DynamicForm },
  
  props: {
    // Service-first API (router-agnostic component)
    service: { type: Object, required: true },
    // Optional UI config (titles, labels). If omitted, derive from service.entity
    config: { type: Object, required: false, default: () => ({}) },
    // External mode control to support inline usage and multi-instances per page
    mode: { type: String, default: 'list' }, // 'list' | 'create' | 'view' | 'edit' | 'delete'
    entityId: { type: [String, Number], default: null },
    displayMode: { 
      type: String, 
      default: 'dialog', // 'inline' | 'dialog'
      validator: v => ['inline', 'dialog'].includes(v)
    },
    showCreateButton: { type: Boolean, default: true }
  },
  
  data() {
    return {
      entities: [],
      loading: false,
      showCreateForm: false,
      showDeleteConfirm: false,
      showBulkDeleteConfirm: false,
      editingEntity: null,
      entityToDelete: null,
      selectedEntities: [],
      deleting: false,
      bulkDeleting: false,
      isEditing: false
    }
  },
  
  computed: {
    dialogTitle() {
      const entity = this.config.entity || this.service?.entity || 'entity'
      return this.isEditing 
        ? `Edit ${entity}` 
        : `Create New ${entity}`
    }
  },
  
  methods: {
    // Load entities
    async loadEntities() {
      this.loading = true
      try {
        const res = await this.service.list()
        const body = res?.data
        this.entities = Array.isArray(body) ? body : (body?.data || [])
      } catch (error) {
        console.error('Error loading entities:', error)
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load data', life: 3000 })
      } finally {
        this.loading = false
      }
    },
    
    // Handle row actions (emit only; parent decides routing or mode changes)
    async handleRowAction({ action, rowData }) {
      switch (action) {
        case 'view':
          this.$emit('view', rowData)
          break
        case 'edit':
          this.editEntity(rowData)
          break
        case 'delete':
          this.deleteEntity(rowData)
          break
        default:
          this.$emit('row-action', { action, rowData })
      }
    },
    
    // Handle bulk actions
    async handleBulkAction({ action, selectedRows }) {
      this.selectedEntities = selectedRows
      
      switch (action) {
        case 'delete':
          this.showBulkDeleteConfirm = true
          break
        case 'export':
          this.exportSelectedData(selectedRows)
          break
      }
    },
    
    // Edit entity
    editEntity(entity) {
      this.editingEntity = { ...entity }
      this.isEditing = true
      this.showCreateForm = true
    },
    
    // Delete entity
    deleteEntity(entity) {
      this.entityToDelete = entity
      this.showDeleteConfirm = true
    },
    
    // Handle form submission
    async handleFormSubmit(formData) {
      try {
        if (this.isEditing) {
          await this.updateEntity(formData)
        } else {
          await this.createEntity(formData)
        }
        
        this.closeDialog()
        this.loadEntities()
        
        this.$toast.add({
          severity: 'success',
          summary: 'Success',
          detail: this.isEditing ? 'Updated successfully' : 'Created successfully',
          life: 3000
        })
      } catch (error) {
        console.error('Form submission error:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Operation failed',
          life: 3000
        })
      }
    },
    
    // Create entity
    async createEntity(formData) {
      const res = await this.service.create(formData)
      return res?.data
    },
    
    // Update entity
    async updateEntity(formData) {
      const res = await this.service.update(this.editingEntity.id, formData)
      return res?.data
    },
    
    // Confirm delete
    async confirmDelete() {
      this.deleting = true
      try {
        await this.service.delete(this.entityToDelete.id)
        this.showDeleteConfirm = false
        this.entityToDelete = null
        this.loadEntities()
        this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Deleted successfully', life: 3000 })
      } catch (error) {
        console.error('Delete error:', error)
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete', life: 3000 })
      } finally {
        this.deleting = false
      }
    },
    
    // Confirm bulk delete
    async confirmBulkDelete() {
      this.bulkDeleting = true
      try {
        const ids = this.selectedEntities.map(entity => entity.id)
        await this.service.bulkDelete(ids)
        this.showBulkDeleteConfirm = false
        this.selectedEntities = []
        this.loadEntities()
        this.$toast.add({ severity: 'success', summary: 'Success', detail: `Deleted ${ids.length} entities successfully`, life: 3000 })
      } catch (error) {
        console.error('Bulk delete error:', error)
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete entities', life: 3000 })
      } finally {
        this.bulkDeleting = false
      }
    },
    
    // Close dialog
    closeDialog() {
      this.showCreateForm = false
      this.editingEntity = null
      this.isEditing = false
    },
    
    // Export data
    exportData() {
      // Implementation for data export
      console.log('Exporting data...')
    },
    
    // Export selected data
    exportSelectedData(selectedRows) {
      // Implementation for selected data export
      console.log('Exporting selected data...', selectedRows)
    }
  },
  
  // Load entities on mount
  mounted() {
    this.loadEntities()
  }
}
</script>

<style scoped>
/* Use PrimeFlex utilities for spacing/layout; avoid custom CSS. */
</style>

## 📋 **CRUD CONFIG INTEGRATION:**

### **Complete Artist CRUD Configuration:**
```javascript
// crud-configs/artist.js
export const artistCrudConfig = {
  entity: 'artist',
  title: 'Artist Management',
  
  // Table configuration
  table: {
    columns: [
      { 
        field: 'name', 
        header: 'Artist Name', 
        sortable: true,
        type: 'text',
        props: { truncate: true, maxLength: 30 }
      },
      { 
        field: 'abbreviation', 
        header: 'Abbr', 
        sortable: true,
        type: 'text',
        props: { class: 'font-mono text-sm' }
      },
      { 
        field: 'albums_count', 
        header: 'Albums', 
        sortable: true,
        type: 'number',
        props: { format: '0,0' }
      },
      { 
        field: 'created_at', 
        header: 'Created', 
        sortable: true,
        type: 'date',
        props: { format: 'MMM DD, YYYY' }
      }
    ],
    actions: ['view', 'edit', 'delete'],
    bulkActions: ['delete', 'export'],
    filters: ['search', 'date_range'],
    sortable: true,
    paginated: true,
    pageSize: 20,
    selectionMode: 'multiple',
    resizable: true,
    striped: true,
    hover: true
  },
  
  // Form configuration (array-based fields)
  form: {
    fields: [
      { key: 'name', type: 'text', label: 'Artist Name', required: true, props: { placeholder: 'Enter artist name', maxLength: 100 } },
      { key: 'abbreviation', type: 'text', label: 'Abbreviation', required: true, props: { placeholder: 'Enter abbreviation', maxLength: 10 } },
      { key: 'persona', type: 'json', label: 'Artist Persona', props: { height: '200px' } },
      { key: 'birth_date', type: 'date', label: 'Birth Date', props: { dateFormat: 'yy-mm-dd', showIcon: true } }
    ]
  },
  
  // Features
  exportEnabled: true
}
```

## 📁 **USAGE:**

### **In Artist Management View:**
```vue
<template>
  <div class="artists-view">
    <CrudManager :config="artistCrudConfig" />
  </div>
</template>

<script>
import CrudManager from '@/components/crud/CrudManager.vue'
import { artistCrudConfig } from '@/configs/crud/artist.js'

export default {
  name: 'ArtistsView',
  components: { CrudManager },
  data() {
    return {
      artistCrudConfig
    }
  }
}
</script>
```

### **In Album Management View:**
```vue
<template>
  <div class="albums-view">
    <CrudManager :config="albumCrudConfig" />
  </div>
</template>

<script>
import CrudManager from '@/components/crud/CrudManager.vue'
import { albumCrudConfig } from '@/configs/crud/album.js'

export default {
  name: 'AlbumsView',
  components: { CrudManager },
  data() {
    return {
      albumCrudConfig
    }
  }
}
</script>
```

## 🎯 **KEY FEATURES:**

### **✅ Complete CRUD Operations:**
- **Create** - Add new entities via modal form
- **Read** - Display entities in configurable table
- **Update** - Edit existing entities via modal form
- **Delete** - Single and bulk delete operations

### **✅ Widget Manager Integration:**
- **DynamicForm** - uses FormWidgetManager for form fields
- **DynamicTable** - uses TableCellWidgetManager for cell rendering
- **Consistent widget system** - same widgets across all contexts

### **✅ Configuration-Driven:**
- **Entity-specific behavior** - different configs per entity type
- **Flexible layouts** - customizable table columns and form fields
- **API integration** - configurable endpoints for all operations

### **✅ User Experience:**
- **Modal-based editing** - inline editing without page navigation
- **Confirmation dialogs** - safe delete operations
- **Toast notifications** - user feedback for all operations
- **Loading states** - visual feedback during operations

**This gives you ONE CRUD component that works for ALL entities with ZERO code duplication!** 

## ⚙️ Mode-driven Rendering (inline vs dialog)

CrudManager is a pure component (no router usage) and supports both inline and dialog rendering via props. Dialogs are optional.

### Props
- **service**: instance of a `CrudService` subclass (required)
- **mode**: `'list' | 'create' | 'view' | 'edit'` (required)
- **entityId?**: `string | number` (used for `view`, `edit`)
- **displayMode?**: `'inline' | 'dialog'` (default: `'inline'`) — applies to create/view/edit only
- **showCreateButton?**: `boolean` (default: `true`)
- **tableConfigOverride?**: object (optional overrides for `service.config.table`)
- **formConfigOverride?**: object (optional overrides for `service.config.form`)
- **fixedFilters?**: object of persistent query params sent to `service.list(...)` (e.g., `{ filter_artist_id: 'eq:123' }`)
- **refField?/refId?**: convenience to auto-build a fixed FK filter (e.g., `refField='artist_id'` + `refId=123` → `{ filter_artist_id: 'eq:123' }`)

### Emits
- **row-action**: `{ action, rowData }`
- **bulk-action**: `{ action, selectedRows }`
- **submit**: `{ payload, mode }` (when create/update is attempted)
- **delete**: `{ id }` (when delete is confirmed)
- **cancel**: `void`
- **success**: `{ operation, data }`
- **error**: `{ operation, error }`

### Behavior by mode
- **list**: renders table only
- **create**: renders form inline; if `displayMode='dialog'`, opens form in dialog
- **view**: renders read-only details inline; if `displayMode='dialog'`, opens in dialog
- **edit**: loads entity by `entityId` and renders form inline; dialog when `displayMode='dialog'`

Delete confirmation
- Single and bulk delete are always confirmed in a dialog. Delete is not a navigable mode and does not change routes. The confirm dialog opens in-place from the current view.

Fixed filters / reference scoping
- `fixedFilters` are always included in calls to `service.list(...)`, independent of UI filters on the table.
- When `refField` and `refId` are provided, they are translated into a persistent FK filter: `filter_<refField>=eq:<refId>`.
- UI filters (search/date/etc.) layer on top of `fixedFilters`.

### Example (inline rendering)
```vue
<template>
  <div class="crud-view">
    <!-- Albums scoped to a specific artist (FK ref) -->
    <!-- Either pass fixedFilters directly: { filter_artist_id: 'eq:123' } -->
    <!-- Or pass sugar props: refField='artist_id' refId=123 -->

    <!-- List -->
    <DynamicTable
      v-if="mode === 'list'"
      :config="service.config.table"
      :data="entities"
      :loading="loading"
      @row-action="$emit('row-action', $event)"
      @bulk-action="$emit('bulk-action', $event)"
    />

    <!-- Create/Edit inline form -->
    <DynamicForm
      v-if="mode === 'create' || mode === 'edit'"
      :config="formConfig"
      :initial-data="mode==='edit' ? currentEntity : {}"
      :submit-label="mode==='edit' ? 'Update' : 'Create'"
      @submit="payload => $emit('submit', { payload, mode })"
      @cancel="$emit('cancel')"
    />

    <!-- View inline details -->
    <div v-if="mode === 'view'" class="view-panel">
      <!-- render read-only fields from form config -->
      <div v-for="f in (formConfig.fields||[])" :key="f.key" v-if="f.key">
        <strong>{{ f.label || f.key }}</strong>: {{ currentEntity?.[f.key] }}
      </div>
    </div>

    <!-- No inline delete bar; delete is handled via a confirmation dialog (see below) -->
  </div>
</template>
```

### Example (dialog rendering)
```vue
<template>
  <Dialog v-model:visible="mode==='create' || mode==='edit'" :header="mode==='edit' ? 'Edit' : 'Create'">
    <DynamicForm
      :config="formConfig"
      :initial-data="mode==='edit' ? currentEntity : {}"
      :submit-label="mode==='edit' ? 'Update' : 'Create'"
      @submit="payload => $emit('submit', { payload, mode })"
      @cancel="$emit('cancel')"
    />
  </Dialog>

  <Dialog v-model:visible="mode==='view'" header="View">
    <div v-for="f in (formConfig.fields||[])" :key="f.key" v-if="f.key">
      <strong>{{ f.label || f.key }}</strong>: {{ currentEntity?.[f.key] }}
    </div>
  </Dialog>

  <!-- Delete confirmation dialog (triggered by delete action) -->
  <Dialog v-model:visible="showDeleteConfirm" header="Confirm Delete">
    <div class="flex align-items-center gap-2">
      <span>Delete this {{ service.entity }}?</span>
      <Button label="Cancel" severity="secondary" @click="$emit('cancel')" />
      <Button label="Delete" severity="danger" @click="$emit('delete', { id: entityId })" />
    </div>
  </Dialog>
</template>
```

## 🧩 CrudPage (View) — Route → Props

- Purpose: a view that composes the existing `Page` component and maps URL to `CrudManager` props. No inheritance needed; composition only.
- Behavior:
  - Reads the current route and computes `{ mode, entityId, displayMode }`.
  - Passes those props to `CrudManager`.
  - Handles navigation on `submit/delete/cancel/success/error` events.
  - Can host multiple `CrudManager` instances (pass different services/props).

### Route examples
- `/artists` → `mode='list'`
- `/artists/new` → `mode='create'`
- `/artists/:id` → `mode='view'`, `entityId=:id`
- `/artists/:id/edit` → `mode='edit'`, `entityId=:id`

### Mobile-first
- Use `Page` to control header/actions; render compact inline tables/forms in `CrudManager`.
- When `displayMode='dialog'`, the dialogs open above the same shell.

Note on delete
- Delete (single and bulk) is confirmed via dialog in-place; do not route to a delete URL. The view listens for delete actions and toggles the confirm dialog.