<template>
  <div class="dynamic-page">
    <Page :title="resolvedTitle" :back="Boolean(config?.header?.back)" :actions="resolvedActions" />
    <DynamicWidgetList
      :items="config?.widgets || []"
      :context="contextResolver"
      :rowClass="config?.layout?.rowClass || 'grid'"
      :gap="config?.layout?.gap || 'gap-3'"
    />
  </div>
</template>

<script>
import DynamicWidgetList from '@/core/dynamic-widget/DynamicWidgetList.vue'
import Page from '@/components/page/Page.vue'
import { useRoute } from 'vue-router'
import { inject, computed } from 'vue'
import PageManager from '@/core/page/PageManager.js'

const DynamicPage = {
  name: 'DynamicPage',
  components: { DynamicWidgetList, Page },

  setup() {
    const route = useRoute()
    
    // Resolve page config from route meta using the existing function
    const config = computed(() => resolveRoutePageConfig(route))

    const resolvedTitle = computed(() => typeof config.value?.header?.title === 'function'
      ? config.value.header.title({ route })
      : (config.value?.header?.title || ''))

    const resolvedActions = computed(() => config.value?.header?.actions || [])

    const contextResolver = () => (typeof config.value?.context === 'function'
      ? config.value.context({ route, inject })
      : (config.value.context || {}))

    return { config, resolvedTitle, resolvedActions, contextResolver }
  }
}

// Static helper on component object
DynamicPage.createRoute = function(path, page, meta = {}) {
  return { path, component: DynamicPage, meta: { page, ...meta } }
}

// Route meta resolver: returns a config object
export function resolveRoutePageConfig(route) {
  const src = route?.meta?.page
  if (typeof src === 'function') return src({ route, inject })
  if (typeof src === 'string') {
    const { component } = PageManager.getWidget(src)
    return component
  }
  return src || { header: { title: '' }, widgets: [] }
}

export default DynamicPage
</script>

<style scoped>
</style>


