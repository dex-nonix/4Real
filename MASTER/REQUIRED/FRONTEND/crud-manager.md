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
    // Service usage (router-agnostic component)
    service: { type: Object, required: true },
    // Optional UI config (titles, labels). If omitted, derive from service.entity
    config: { type: Object, required: false, default: () => ({}) },
    // External mode control to support inline usage and multi-instances per page
    mode: { type: String, default: 'list' }, // 'list' | 'create' | 'view' | 'edit'
    entityId: { type: [String, Number], default: null },
    displayMode: { 
      type: String, 
      default: 'inline', // 'inline' | 'dialog'
      validator: v => ['inline', 'dialog'].includes(v)
    },
    showCreateButton: { type: Boolean, default: true }
  },
  
  data() {
    return {
      entities: [],
      loading: false,
      showDeleteConfirm: false,
      showBulkDeleteConfirm: false,
      currentEntity: null,
      entityToDelete: null,
      selectedEntities: [],
      deleting: false,
      bulkDeleting: false
    }
  },
  
  computed: {
    dialogTitle() {
      const entity = this.config.entity || this.service?.entity || 'entity'
      return this.mode === 'edit' 
        ? `Edit ${entity}` 
        : `Create New ${entity}`
    }
  },
  
  methods: {
    // Load entities (includes fixedFilters/refField/refId when provided)
    async loadEntities() {
      this.loading = true
      try {
        const query = { ...(this.fixedFilters || {}) }
        if (this.refField && this.refId != null) {
          query[`filter_${this.refField}`] = `eq:${this.refId}`
        }
        const res = await this.service.list(query)
        const body = res?.data
        this.entities = Array.isArray(body) ? body : (body?.data || [])
      } catch (error) {
        console.error('Error loading entities:', error)
      } finally {
        this.loading = false
      }
    },
    
    // Handle row actions (emit only; parent sets mode/routing)
    async handleRowAction({ action, rowData }) {
      this.$emit('row-action', { action, rowData })
      if (action === 'delete') {
        this.entityToDelete = rowData
        this.showDeleteConfirm = true
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
    
    // Handle form submission (internal; executes service call)
    async handleFormSubmit(formData) {
      try {
        if (this.mode === 'edit' && (this.entityId != null || this.currentEntity?.id != null)) {
          const id = this.entityId ?? this.currentEntity.id
          await this.service.update(id, formData)
          if (this.$toast?.add) this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Updated successfully', life: 3000 })
          this.$emit?.('success', { operation: 'update', data: { id } })
        } else {
          await this.service.create(formData)
          if (this.$toast?.add) this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Created successfully', life: 3000 })
          this.$emit?.('success', { operation: 'create', data: null })
        }
        await this.loadEntities()
      } catch (error) {
        if (this.$toast?.add) this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Operation failed', life: 3000 })
        this.$emit?.('error', { operation: this.mode === 'edit' ? 'update' : 'create', error })
      }
    },
    
    // Confirm delete (internal; executes service call)
    async confirmDelete() {
      if (!this.entityToDelete?.id) {
        this.showDeleteConfirm = false
        return
      }
      this.deleting = true
      try {
        await this.service.delete(this.entityToDelete.id)
        this.showDeleteConfirm = false
        this.entityToDelete = null
        await this.loadEntities()
        if (this.$toast?.add) this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Deleted successfully', life: 3000 })
        this.$emit?.('success', { operation: 'delete', data: null })
      } catch (error) {
        if (this.$toast?.add) this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete', life: 3000 })
        this.$emit?.('error', { operation: 'delete', error })
      } finally {
        this.deleting = false
      }
    },

    // Load current entity for view/edit
    async loadCurrentEntity() {
      const id = this.entityId
      if (id == null) return
      try {
        const res = await this.service.get(id)
        const body = res?.data
        this.currentEntity = body?.data || body || null
      } catch (error) {
        // no-op toast optional
      }
    },
    
    // Confirm bulk delete (internal; executes service call)
    async confirmBulkDelete() {
      const ids = this.selectedEntities.map(e => e.id).filter(v => v != null)
      if (!ids.length) {
        this.showBulkDeleteConfirm = false
        return
      }
      this.bulkDeleting = true
      try {
        await this.service.bulkDelete(ids)
        this.showBulkDeleteConfirm = false
        this.selectedEntities = []
        await this.loadEntities()
        if (this.$toast?.add) {
          this.$toast.add({ severity: 'success', summary: 'Success', detail: `Deleted ${ids.length} items`, life: 3000 })
        }
        this.$emit?.('success', { operation: 'bulk-delete', data: { ids } })
      } catch (error) {
        if (this.$toast?.add) {
          this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete items', life: 3000 })
        }
        this.$emit?.('error', { operation: 'bulk-delete', error })
      } finally {
        this.bulkDeleting = false
      }
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
    if (this.mode === 'view' || this.mode === 'edit') {
      this.loadCurrentEntity()
    }
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

## 📁 **USAGE (Provide/Inject + CrudPage + Route Meta):**

### Provide singletons (inline) at app bootstrap
```js
// src/main.js
import ArtistService from '@/services/ArtistService.js'
import AlbumService from '@/services/AlbumService.js'
import TrackService from '@/services/TrackService.js'
import PersonaService from '@/services/PersonaService.js'
import InternalToolService from '@/services/InternalToolService.js'
import PersonaToolAccessService from '@/services/PersonaToolAccessService.js'
import MCPServerService from '@/services/MCPServerService.js'
import PersonaMCPServerService from '@/services/PersonaMCPServerService.js'
import ChatSessionService from '@/services/ChatSessionService.js'
import ChatMessageService from '@/services/ChatMessageService.js'
import ToolInvocationLogService from '@/services/ToolInvocationLogService.js'

// ... create app, use router/PrimeVue/ToastService

// Provide service singletons (inline, no temp vars)
app.provide('artists', new ArtistService())
app.provide('albums', new AlbumService())
app.provide('tracks', new TrackService())
app.provide('personas', new PersonaService())
app.provide('internal-tools', new InternalToolService())
app.provide('persona-tool-access', new PersonaToolAccessService())
app.provide('mcp-servers', new MCPServerService())
app.provide('persona-mcp-servers', new PersonaMCPServerService())
app.provide('chat-sessions', new ChatSessionService())
app.provide('chat-messages', new ChatMessageService())
app.provide('tool-invocation-logs', new ToolInvocationLogService())
```

### DO NOT handcraft CRUD routes manually
- Always use `CrudPage.createRoutes(...)` to generate the standard CRUD paths.
- This guarantees consistent meta and prevents drift.

### Static route builder (CrudPage.createRoutes)
```js
// src/router/index.js (excerpt)
import CrudPage from '@/pages/CrudPage.vue'

// Returns an array with standard CRUD routes for the key
const routes = [
  ...CrudPage.createRoutes('artists', {
    displayMode: 'inline',
    // Optional extras passed into meta.crud and consumed by CrudPage/CrudManager:
    // fixedFilters: { filter_status: 'eq:active' },
    // refField: 'artist_id', refId: 123,
    // showCreateButton: true,
    // tableConfigOverride: { pageSize: 50 },
    // formConfigOverride: { fields: [...] },
    // basePath: '/artists' // default is `/${entityKey}`
  }),
  ...CrudPage.createRoutes('albums', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('personas'),
  ...CrudPage.createRoutes('internal-tools'),
  ...CrudPage.createRoutes('persona-tool-access'),
  ...CrudPage.createRoutes('mcp-servers'),
  ...CrudPage.createRoutes('persona-mcp-servers'),
  ...CrudPage.createRoutes('chat-sessions'),
  ...CrudPage.createRoutes('chat-messages'),
  ...CrudPage.createRoutes('tool-invocation-logs'),
]
```

#### API: CrudPage.createRoutes(entityKey, options?, meta?) → Route[]
- **Purpose**: Generate the standard CRUD routes for a single entity, with normalized meta used by `CrudPage` and `CrudManager`.
- **Parameters**
  - **entityKey** (string): Injection key for the singleton service (e.g., `'artists'`, `'albums'`). Must match `app.provide('<key>', new Service())`.
  - **options** (object, optional): Controls builder and passes CRUD-specific meta under `meta.crud`.
    - **displayMode**: `'inline' | 'dialog'` (default `'inline'`).
    - **basePath**: string (default `/${entityKey}`) to change the base URL segment.
    - Passed into `meta.crud` (consumed by `CrudPage`/`CrudManager`):
      - **fixedFilters**, **refField**, **refId**, **showCreateButton**, **tableConfigOverride**, **formConfigOverride**.
  - **meta** (object, optional): Top-level route meta merged into each route. Default is `{ layout: 'master' }`.
- **Returns**: An array of 4 route records:
  - `/<basePath>` (list), `/<basePath>/new` (create), `/<basePath>/:id` (view), `/<basePath>/:id/edit` (edit)
- **Notes**
  - Delete is not routed; it is always confirmed and executed inside `CrudManager`.
  - `CrudPage` reads the `meta.crud.key` to `inject(key)` the correct singleton service.

Example with custom layout meta:
```js
const routes = [
  ...CrudPage.createRoutes('artists', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('albums', { displayMode: 'dialog' }, { layout: 'master' })
]
```

### CrudPage resolves injected service by meta and maps route → props
```vue
<!-- src/pages/CrudPage.vue (concept) -->
<script setup>
import { inject, computed } from 'vue'
import { useRoute } from 'vue-router'
import CrudManager from '@/components/crud/CrudManager.vue'

const route = useRoute()
const cfg = route.meta?.crud || {}
const service = inject(cfg.key)

const mode = computed(() => {
  if (route.path.endsWith('/new')) return 'create'
  if (route.path.endsWith('/edit')) return 'edit'
  return route.params.id ? 'view' : 'list'
})
const entityId = computed(() => route.params.id || null)
const displayMode = computed(() => cfg.displayMode || 'inline')
</script>

<template>
  <CrudManager :service="service" :mode="mode" :entity-id="entityId" :display-mode="displayMode" />
  <!-- Delete confirmations are always handled by CrudManager dialogs -->
  <!-- Routing changes happen outside via row-action (view/edit/create) if needed -->
</template>
```

## 🎯 **KEY FEATURES:**

### **✅ Complete CRUD Operations:**
- **Create** - Add new entities via modal form
- **Read** - Display entities in configurable table
- **Update** - Edit existing entities via modal form
- **Delete** - Single and bulk delete operations

### **✅ Widget Manager Integration:**
- **DynamicForm** - uses EditWidgetManager (edit) and DisplayWidgetManager (display)
- **DynamicTable** - uses DisplayWidgetManager for cell rendering
- **Consistent widget system** - same display widgets across contexts

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

### Emits (optional)
- **row-action**: `{ action, rowData }` (useful if parent wants to change route/mode)
- **cancel**: `void`
- **success**: `{ operation, data }` (optional notification)
- **error**: `{ operation, error }` (optional notification)

### Behavior by mode
- **list**: renders table only
- **create**: renders form inline; if `displayMode='dialog'`, opens form in dialog
- **view**: renders read-only details inline; if `displayMode='dialog'`, opens in dialog
- **edit**: loads entity by `entityId` and renders form inline; dialog when `displayMode='dialog'`

Delete confirmation
- Single and bulk delete are always confirmed in a dialog and executed internally by CrudManager. Delete is not a navigable mode and does not change routes. The confirm dialog opens in-place from the current view.

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
      @submit="handleFormSubmit"
      @cancel="$emit('cancel')"
    />

    <!-- View inline details -->
    <DynamicForm
      v-if="mode === 'view'"
      :config="formConfig"
      :initial-data="currentEntity || {}"
      mode="display"
    />

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
      @submit="handleFormSubmit"
      @cancel="$emit('cancel')"
    />
  </Dialog>

  <Dialog v-model:visible="mode==='view'" header="View">
    <DynamicForm :config="formConfig" :initial-data="currentEntity || {}" mode="display" />
  </Dialog>

  <!-- Delete confirmation dialog (triggered by delete action) -->
  <Dialog v-model:visible="showDeleteConfirm" header="Confirm Delete">
    <div class="flex align-items-center gap-2">
      <span>Delete this {{ service.entity }}?</span>
      <Button label="Cancel" severity="secondary" @click="$emit('cancel')" />
      <Button label="Delete" severity="danger" @click="confirmDelete" />
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