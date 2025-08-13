<template>
  <div class="crud-manager">
    <div class="crud-header flex justify-content-between align-items-center mb-4">
      <h1>{{ title || `${entityTitle} Management` }}</h1>

      <div class="header-actions flex gap-3">
        <Button
          @click="showCreateForm = true"
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

    <Dialog
      v-model:visible="showCreateForm"
      :header="dialogTitle"
      :modal="true"
      :closable="true"
      :close-on-escape="true"
      :style="{ width: '50vw' }"
    >
      <DynamicForm
        :config="formConfig"
        :initial-data="editingEntity"
        :submit-label="isEditing ? 'Update' : 'Create'"
        @submit="handleFormSubmit"
        @cancel="closeDialog"
      />
    </Dialog>

    <Dialog
      v-model:visible="showViewDialog"
      :header="`View ${entitySingular}`"
      :modal="true"
      :closable="true"
      :close-on-escape="true"
      :style="{ width: '40vw' }"
      @hide="onViewHide"
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
    service: {
      type: Object,
      required: true
    },
    title: {
      type: String,
      default: ''
    }
  },

  data() {
    return {
      entities: [],
      loading: false,
      showCreateForm: false,
      showViewDialog: false,
      showDeleteConfirm: false,
      showBulkDeleteConfirm: false,
      editingEntity: null,
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
      return this.config.table || {}
    },
    formConfig() {
      return this.config.form || { fields: [] }
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
      return this.isEditing ? `Edit ${this.entitySingular}` : `Create New ${this.entitySingular}`
    }
  },

  methods: {
    async loadEntities() {
      this.loading = true
      try {
        const res = await this.service.list()
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
          this.openView(rowData)
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
      this.isEditing = true
      this.showCreateForm = true
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
        // Sync URL query (?view=<id>)
        if (this.$router && this.$route) {
          const q = { ...(this.$route.query || {}), view: String(id) }
          this.$router.replace({ query: q })
        }
      } catch (error) {
        this.notifyError('Failed to load item')
        // eslint-disable-next-line no-console
        console.error('View load error:', error)
      }
    },

    async openViewById(id) {
      if (id == null) return
      await this.openView({ id })
    },

    closeView() {
      this.showViewDialog = false
      this.viewingEntity = null
      // Clear URL query param
      if (this.$router && this.$route) {
        const { view, ...rest } = this.$route.query || {}
        this.$router.replace({ query: rest })
      }
    },

    onViewHide() {
      // Ensure URL cleanup when dialog closes via escape/close icon
      if (this.showViewDialog === false) {
        if (this.$router && this.$route) {
          const { view, ...rest } = this.$route.query || {}
          this.$router.replace({ query: rest })
        }
      }
    },

    async handleFormSubmit(formData) {
      try {
        if (this.isEditing && this.editingEntity?.id != null) {
          await this.service.update(this.editingEntity.id, formData)
          this.notifySuccess('Updated successfully')
        } else {
          await this.service.create(formData)
          this.notifySuccess('Created successfully')
        }
        this.closeDialog()
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

    closeDialog() {
      this.showCreateForm = false
      this.editingEntity = null
      this.isEditing = false
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
    // If URL carries ?view=<id>, open view dialog automatically
    const viewId = this.$route && this.$route.query ? this.$route.query.view : null
    if (viewId != null) {
      const asNum = Number(viewId)
      this.openViewById(Number.isNaN(asNum) ? viewId : asNum)
    }
  }
}
</script>

<style scoped>
/* Use PrimeFlex utilities for spacing/layout; avoid custom CSS. */
</style>


