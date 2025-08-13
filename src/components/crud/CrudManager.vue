<template>
  <div class="crud-manager">
    <div class="crud-header flex justify-content-between align-items-center mb-4">
      <h1>{{ title || `${entityTitle} Management` }}</h1>

      <div class="header-actions flex gap-3">
        <Button
          v-if="showCreateButton"
          @click="onAddNew"
          icon="pi pi-plus"
          label="Add New"
        />

        <Button
          v-if="exportEnabled"
          @click="exportData"
          icon="pi pi-download"
          severity="secondary"
          label="Export"
        />
      </div>
    </div>

    <DynamicTable
      :config="tableConfig"
      :data="entities"
      :loading="loading"
      @row-action="handleRowAction"
      @bulk-action="handleBulkAction"
    />

    <!-- Inline create/edit form when displayMode is inline -->
    <div v-if="displayMode === 'inline' && (isCreateMode || isEditMode)" class="mt-3">
      <DynamicForm
        :config="formConfig"
        :initial-data="isEditMode ? currentEntity : {}"
        :submit-label="isEditMode ? 'Update' : 'Create'"
        @submit="handleFormSubmit"
      />
    </div>

    <!-- Inline view panel when displayMode is inline -->
    <div v-if="displayMode === 'inline' && isViewMode" class="view-panel mt-3">
      <div v-for="f in (formConfig.fields || [])" :key="f.key" v-if="f && f.key" class="mb-2">
        <strong>{{ f.label || f.key }}</strong>: {{ currentEntity ? currentEntity[f.key] : '' }}
      </div>
    </div>

    <Dialog
      v-if="displayMode === 'dialog'"
      v-model:visible="formDialogVisible"
      :header="dialogTitle"
      :modal="true"
      :closable="true"
      :close-on-escape="true"
      :style="{ width: '50vw' }"
    >
      <DynamicForm
        :config="formConfig"
        :initial-data="editingEntity || {}"
        :submit-label="editingEntity ? 'Update' : 'Create'"
        @submit="handleFormSubmit"
        @cancel="closeFormDialog"
      />
    </Dialog>

    <Dialog
      v-if="displayMode === 'dialog'"
      v-model:visible="showViewDialog"
      :header="`View ${entitySingular}`"
      :modal="true"
      :closable="true"
      :close-on-escape="true"
      :style="{ width: '40vw' }"
    >
      <div v-if="viewingEntity" class="view-details flex flex-column gap-3">
        <div
          v-for="field in viewFields"
          :key="field.key"
          class="flex justify-content-between align-items-start gap-3"
        >
          <span class="font-medium">{{ field.label || field.key }}</span>
          <span class="text-color-secondary">{{ formatValue(field, viewingEntity[field.key]) }}</span>
        </div>
      </div>
      <template #footer>
        <Button label="Close" severity="secondary" @click="closeView" />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="showDeleteConfirm"
      header="Confirm Delete"
      :modal="true"
      :closable="true"
      :style="{ width: '30vw' }"
    >
      <div class="delete-confirmation">
        <p>Are you sure you want to delete this {{ entitySingular }}?</p>
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

    <Dialog
      v-model:visible="showBulkDeleteConfirm"
      header="Confirm Bulk Delete"
      :modal="true"
      :closable="true"
      :style="{ width: '30vw' }"
    >
      <div class="bulk-delete-confirmation">
        <p>Are you sure you want to delete {{ selectedEntities.length }} {{ entityPlural }}?</p>
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
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import DynamicTable from '@/components/tables/DynamicTable.vue'
import DynamicForm from '@/components/forms/DynamicForm.vue'

export default {
  name: 'CrudManager',
  components: { Dialog, Button, DynamicTable, DynamicForm },

  props: {
    service: { type: Object, required: true },
    title: { type: String, default: '' },
    mode: { type: String, default: 'list' }, // 'list' | 'create' | 'view' | 'edit'
    entityId: { type: [String, Number], default: null },
    displayMode: { type: String, default: 'inline' }, // 'inline' | 'dialog'
    showCreateButton: { type: Boolean, default: true },
    tableConfigOverride: { type: Object, default: () => ({}) },
    formConfigOverride: { type: Object, default: () => ({}) },
    fixedFilters: { type: Object, default: () => ({}) },
    refField: { type: String, default: '' },
    refId: { type: [String, Number], default: null }
  },

  data() {
    return {
      entities: [],
      loading: false,
      formDialogVisible: false,
      showViewDialog: false,
      showDeleteConfirm: false,
      showBulkDeleteConfirm: false,
      editingEntity: null,
      currentEntity: null,
      viewingEntity: null,
      entityToDelete: null,
      selectedEntities: [],
      deleting: false,
      bulkDeleting: false,
      isEditing: false
    }
  },

  computed: {
    config() {
      return this.service?.config || {}
    },
    tableConfig() {
      return { ...(this.config.table || {}), ...(this.tableConfigOverride || {}) }
    },
    formConfig() {
      const base = this.config.form || { fields: [] }
      const override = this.formConfigOverride || {}
      return { ...base, ...override, fields: override.fields || base.fields }
    },
    exportEnabled() {
      return Boolean(this.config.exportEnabled)
    },
    viewFields() {
      const fields = Array.isArray(this.formConfig.fields) ? this.formConfig.fields : []
      return fields.filter(f => f && f.key)
    },
    entityTitle() {
      const raw = this.config.entity || this.service?.entity || 'Entity'
      return String(raw).charAt(0).toUpperCase() + String(raw).slice(1)
    },
    entitySingular() {
      return this.config.entity || this.service?.entity || 'entity'
    },
    entityPlural() {
      const base = this.entitySingular
      if (base.endsWith('s')) return base
      return `${base}s`
    },
    dialogTitle() {
      return this.isEditMode ? `Edit ${this.entitySingular}` : `Create New ${this.entitySingular}`
    },
    isListMode() {
      return this.mode === 'list'
    },
    isCreateMode() {
      return this.mode === 'create'
    },
    isViewMode() {
      return this.mode === 'view'
    },
    isEditMode() {
      return this.mode === 'edit'
    }
  },

  methods: {
    async loadEntities() {
      this.loading = true
      try {
        const query = { ...(this.fixedFilters || {}) }
        if (this.refField && this.refId != null) {
          query[`filter_${this.refField}`] = `eq:${this.refId}`
        }
        const res = await this.service.list(query)
        const body = res?.data
        const list = Array.isArray(body) ? body : body?.data
        this.entities = Array.isArray(list) ? list : []
      } catch (error) {
        this.notifyError('Failed to load data')
        // eslint-disable-next-line no-console
        console.error('Error loading entities:', error)
      } finally {
        this.loading = false
      }
    },

    async handleRowAction({ action, rowData }) {
      switch (action) {
        case 'view':
          if (this.displayMode === 'dialog') {
            this.openView(rowData)
          } else {
            this.$emit('row-action', { action, rowData })
          }
          break
        case 'edit':
          if (this.displayMode === 'dialog') {
            this.editEntity(rowData)
          } else {
            this.$emit('row-action', { action, rowData })
          }
          break
        case 'delete':
          this.deleteEntity(rowData)
          break
        default:
          this.$emit('row-action', { action, rowData })
      }
    },

    async handleBulkAction({ action, selectedRows }) {
      this.selectedEntities = selectedRows || []
      switch (action) {
        case 'delete':
          this.showBulkDeleteConfirm = true
          break
        case 'export':
          this.exportSelectedData(this.selectedEntities)
          break
        default:
          this.$emit('bulk-action', { action, selectedRows: this.selectedEntities })
      }
    },

    editEntity(entity) {
      this.editingEntity = { ...entity }
      this.formDialogVisible = true
    },

    deleteEntity(entity) {
      this.entityToDelete = entity
      this.showDeleteConfirm = true
    },

    async openView(entity) {
      try {
        const id = entity?.id
        if (id == null) return
        // Fetch latest details
        const res = await this.service.get(id)
        const body = res?.data
        const obj = body?.data || body
        this.viewingEntity = obj || entity
        this.showViewDialog = true
      } catch (error) {
        this.notifyError('Failed to load item')
        // eslint-disable-next-line no-console
        console.error('View load error:', error)
      }
    },

    closeView() {
      this.showViewDialog = false
      this.viewingEntity = null
    },

    onAddNew() {
      if (this.displayMode === 'dialog') {
        this.editingEntity = null
        this.formDialogVisible = true
      } else {
        this.$emit('row-action', { action: 'create' })
      }
    },

    async handleFormSubmit(formData) {
      try {
        if ((this.displayMode === 'dialog' && this.editingEntity?.id != null) || this.isEditMode) {
          const id = this.editingEntity?.id ?? this.entityId
          await this.service.update(id, formData)
          this.notifySuccess('Updated successfully')
        } else {
          await this.service.create(formData)
          this.notifySuccess('Created successfully')
        }
        this.closeFormDialog()
        await this.loadEntities()
      } catch (error) {
        this.notifyError('Operation failed')
        // eslint-disable-next-line no-console
        console.error('Form submission error:', error)
      }
    },

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
        this.notifySuccess('Deleted successfully')
      } catch (error) {
        this.notifyError('Failed to delete')
        // eslint-disable-next-line no-console
        console.error('Delete error:', error)
      } finally {
        this.deleting = false
      }
    },

    async confirmBulkDelete() {
      const ids = (this.selectedEntities || []).map(e => e.id).filter(v => v != null)
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
        this.notifySuccess(`Deleted ${ids.length} ${this.entityPlural}`)
      } catch (error) {
        this.notifyError('Failed to delete entities')
        // eslint-disable-next-line no-console
        console.error('Bulk delete error:', error)
      } finally {
        this.bulkDeleting = false
      }
    },

    closeFormDialog() {
      this.formDialogVisible = false
      this.editingEntity = null
    },

    exportData() {
      this.$emit('export-all', { data: this.entities })
    },

    exportSelectedData(selectedRows) {
      this.$emit('export-selected', { data: selectedRows })
    },

    notifySuccess(detail) {
      if (this.$toast && typeof this.$toast.add === 'function') {
        this.$toast.add({ severity: 'success', summary: 'Success', detail, life: 3000 })
      }
    },

    notifyError(detail) {
      if (this.$toast && typeof this.$toast.add === 'function') {
        this.$toast.add({ severity: 'error', summary: 'Error', detail, life: 3000 })
      }
    }
  },

  mounted() {
    this.loadEntities()
    if ((this.isViewMode || this.isEditMode) && this.entityId != null) {
      // Load current entity for inline modes
      this.service.get(this.entityId).then(res => {
        const body = res?.data
        this.currentEntity = body?.data || body || null
      }).catch(() => {})
    }
  }
}
</script>

<style scoped>
/* Use PrimeFlex utilities for spacing/layout; avoid custom CSS. */
</style>


