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

<script>
import { inject, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CrudManager from '@/components/crud/CrudManager.vue'

const CrudPage = {
  name: 'CrudPage',
  components: { CrudManager },
  setup() {
    const route = useRoute()
    const router = useRouter()

    const cfg = route.meta?.crud || {}
    const service = inject(cfg.key)

    const mode = computed(() => {
      const p = route.path || ''
      if (p.endsWith('/new')) return 'create'
      if (p.endsWith('/edit')) return 'edit'
      return route.params?.id ? 'view' : 'list'
    })

    const entityId = computed(() => route.params?.id || null)
    const displayMode = computed(() => cfg.displayMode || 'inline')

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

    function handleSuccess() {}
    function handleError() {}

    return {
      service,
      mode,
      entityId,
      displayMode,
      fixedFilters,
      refField,
      refId,
      showCreateButton,
      tableConfigOverride,
      formConfigOverride,
      handleRowAction,
      handleSuccess,
      handleError,
    }
  }
}

// Static helper to add CRUD routes for an entity key
CrudPage.createRoutes = function createRoutes(entityKey, options = {}, meta = { layout: 'master' }) {
  const { basePath: bp, displayMode: dm = 'inline', ...crud } = options || {}
  const basePath = bp || `/${entityKey}`
  const displayMode = dm || 'inline'
  const metaBase = { ...meta, crud: { key: entityKey, displayMode, ...crud } }
  return [
    { path: `${basePath}`, component: CrudPage, meta: metaBase },
    { path: `${basePath}/new`, component: CrudPage, meta: metaBase },
    { path: `${basePath}/:id`, component: CrudPage, meta: metaBase },
    { path: `${basePath}/:id/edit`, component: CrudPage, meta: metaBase }
  ]
}

export default CrudPage
</script>

<style scoped>
.crud-page { width: 100%; }
</style>


