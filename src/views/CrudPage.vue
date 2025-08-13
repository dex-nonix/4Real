<template>
  <div class="crud-page">
    <CrudManager
      :service="service"
      :mode="mode"
      :entity-id="entityId"
      :display-mode="displayMode"
      :show-create-button="showCreateButton"
      :fixed-filters="fixedFilters"
      :ref-field="refField"
      :ref-id="refId"
      :table-config-override="tableConfigOverride"
      :form-config-override="formConfigOverride"
      @row-action="handleRowAction"
      @success="handleSuccess"
      @error="handleError"
    />
  </div>
  </template>

<script setup>
import { inject, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CrudManager from '@/components/crud/CrudManager.vue'

const route = useRoute()
const router = useRouter()

// Read CRUD config from route meta
const cfg = route.meta?.crud || {}

// Inject singleton service by meta key
const service = inject(cfg.key)

// Derive mode from route
const mode = computed(() => {
  const p = route.path || ''
  if (p.endsWith('/new')) return 'create'
  if (p.endsWith('/edit')) return 'edit'
  return route.params?.id ? 'view' : 'list'
})

const entityId = computed(() => route.params?.id || null)
const displayMode = computed(() => cfg.displayMode || 'inline')

// Optional overrides from meta
const fixedFilters = computed(() => cfg.fixedFilters || null)
const refField = computed(() => cfg.refField || '')
const refId = computed(() => cfg.refId ?? null)
const showCreateButton = computed(() => cfg.showCreateButton ?? true)
const tableConfigOverride = computed(() => cfg.tableConfigOverride || null)
const formConfigOverride = computed(() => cfg.formConfigOverride || null)

const entitySingular = computed(() => service?.entity || 'entity')
const entityPlural = computed(() =>
  String(entitySingular.value).endsWith('s') ? String(entitySingular.value) : `${entitySingular.value}s`
)

function handleRowAction({ action, rowData }) {
  const id = rowData?.id
  const base = `/${entityPlural.value}`
  switch (action) {
    case 'create':
      router.push(`${base}/new`)
      break
    case 'view':
      if (id != null) router.push(`${base}/${id}`)
      break
    case 'edit':
      if (id != null) router.push(`${base}/${id}/edit`)
      break
    default:
      break
  }
}

function handleSuccess() {
  // Optional: global notification hook if desired
}

function handleError() {
  // Optional: global error hook if desired
}
</script>

<style scoped>
.crud-page { width: 100%; }
</style>


