<template>
  <div class="crud-page">
    <NxDynamicWidgetList
        v-if="viewBefore && viewBefore.length"
        :items="viewBefore"
        :context="widgetContextResolver"
        class="mb-3"
    />
    <NxCrudManager
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
    <NxDynamicWidgetList
        v-if="viewAfter && viewAfter.length"
        :items="viewAfter"
        :context="widgetContextResolver"
        class="mt-3"
    />
  </div>
</template>

<script>
import {computed, inject} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import NxCrudManager from '@nonix-crud/components/NxCrudManager.vue'
import NxDynamicWidgetList from '@nonix-dynamic/widget/components/NxDynamicWidgetList.vue'

const CrudPage = {
  name: 'NxCrudPage',
  components: {NxCrudManager, NxDynamicWidgetList},
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

    // Dynamic widgets: before/after lists from service config
    const viewBefore = computed(() => service?.config?.view?.before || [])
    const viewAfter = computed(() => service?.config?.view?.after || [])

    // Dynamic widget context resolver (evaluated by the list)
    const widgetContextResolver = () => ({
      service,
      mode: mode.value,
      entityId: entityId.value,
      entity: entitySingular.value,
      entitySingular: entitySingular.value,
      entityPlural: entityPlural.value
    })

    function handleRowAction({action, rowData}) {
      const id = rowData?.id
      const base = `/${entityPlural.value}`
      switch (action) {
        case 'create':
          router.push(`${base}/new`)
          break
        case 'cancel':
          router.push(`${base}`)
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
    }

    function handleError() {
    }

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
      viewBefore,
      viewAfter,
      widgetContextResolver,
      handleRowAction,
      handleSuccess,
      handleError,
    }
  }
}

// Static helper to add CRUD routes for an entity key
CrudPage.createRoutes = function createRoutes(entityKey, options = {}, meta = {layout: 'advanced'}) {
  const {basePath: bp, displayMode: dm = 'inline', ...crud} = options || {}
  const basePath = bp || `/${entityKey}`
  const displayMode = dm || 'inline'
  const metaBase = {...meta, crud: {key: entityKey, displayMode, ...crud}}
  return [
    {path: `${basePath}`, component: CrudPage, meta: metaBase},
    {path: `${basePath}/new`, component: CrudPage, meta: metaBase},
    {path: `${basePath}/:id`, component: CrudPage, meta: metaBase},
    {path: `${basePath}/:id/edit`, component: CrudPage, meta: metaBase}
  ]
}

export default CrudPage
</script>

<style scoped>
.crud-page {
  width: 100%;
}
</style>


