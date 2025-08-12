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
    <div class="crud-header">
      <h1>{{ config.title || `${config.entity} Management` }}</h1>
      
      <div class="header-actions">
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
import DynamicTable from '@/components/core/DynamicTable.vue'
import DynamicForm from '@/components/core/DynamicForm.vue'

export default {
  name: 'CrudManager',
  components: { Dialog, Button, DynamicTable, DynamicForm },
  
  props: {
    config: {
      type: Object,
      required: true
    }
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
      return this.isEditing 
        ? `Edit ${this.config.entity}` 
        : `Create New ${this.config.entity}`
    }
  },
  
  methods: {
    // Load entities
    async loadEntities() {
      this.loading = true
      try {
        const response = await this.$api.get(this.config.api.endpoints.list)
        this.entities = response.data
      } catch (error) {
        console.error('Error loading entities:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load data',
          life: 3000
        })
      } finally {
        this.loading = false
      }
    },
    
    // Handle row actions
    async handleRowAction({ action, rowData }) {
      switch (action) {
        case 'view':
          this.$router.push(`/${this.config.entity}s/${rowData.id}`)
          break
        case 'edit':
          this.editEntity(rowData)
          break
        case 'delete':
          this.deleteEntity(rowData)
          break
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
      const response = await this.$api.post(this.config.api.endpoints.create, formData)
      return response.data
    },
    
    // Update entity
    async updateEntity(formData) {
      const response = await this.$api.put(
        this.config.api.endpoints.update.replace('{id}', this.editingEntity.id), 
        formData
      )
      return response.data
    },
    
    // Confirm delete
    async confirmDelete() {
      this.deleting = true
      try {
        await this.$api.delete(
          this.config.api.endpoints.delete.replace('{id}', this.entityToDelete.id)
        )
        
        this.showDeleteConfirm = false
        this.entityToDelete = null
        this.loadEntities()
        
        this.$toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Deleted successfully',
          life: 3000
        })
      } catch (error) {
        console.error('Delete error:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete',
          life: 3000
        })
      } finally {
        this.deleting = false
      }
    },
    
    // Confirm bulk delete
    async confirmBulkDelete() {
      this.bulkDeleting = true
      try {
        const ids = this.selectedEntities.map(entity => entity.id)
        await this.$api.post(this.config.api.endpoints.bulkDelete, { ids })
        
        this.showBulkDeleteConfirm = false
        this.selectedEntities = []
        this.loadEntities()
        
        this.$toast.add({
          severity: 'success',
          summary: 'Success',
          detail: `Deleted ${ids.length} entities successfully`,
          life: 3000
        })
      } catch (error) {
        console.error('Bulk delete error:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete entities',
          life: 3000
        })
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
.crud-manager {
  padding: 1rem;
}

.crud-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.delete-confirmation,
.bulk-delete-confirmation {
  text-align: center;
}

.entity-name {
  font-weight: bold;
  color: #ef4444;
}

.warning {
  color: #f59e0b;
  font-weight: 500;
}
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
  
  // Form configuration
  form: {
    fields: {
      name: {
        type: 'text',
        label: 'Artist Name',
        required: true,
        props: { placeholder: 'Enter artist name', maxLength: 100 }
      },
      abbreviation: {
        type: 'text',
        label: 'Abbreviation',
        required: true,
        props: { placeholder: 'Enter abbreviation', maxLength: 10 }
      },
      persona: {
        type: 'rich_text',
        label: 'Artist Persona',
        props: { height: '200px', toolbar: ['bold', 'italic', 'underline'] }
      },
      birth_date: {
        type: 'date',
        label: 'Birth Date',
        props: { dateFormat: 'yy-mm-dd', showIcon: true }
      }
    }
  },
  
  // API configuration
  api: {
    endpoints: {
      list: '/api/artists',
      create: '/api/artists',
      update: '/api/artists/{id}',
      delete: '/api/artists/{id}',
      get: '/api/artists/{id}',
      bulkDelete: '/api/artists/bulk-delete'
    }
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