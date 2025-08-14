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
import DynamicWidgetList from '@/components/widgets/DynamicWidgetList.vue'
import Page from '@/components/page/Page.vue'
import { useRoute } from 'vue-router'
import { inject, computed } from 'vue'
import PageManager from '@/pages/PageManager.js'

const DynamicPage = {
  name: 'DynamicPage',
  components: { DynamicWidgetList, Page },
  props: { config: { type: Object, required: true } },
  setup(props) {
    const route = useRoute()

    const resolvedTitle = computed(() => typeof props.config?.header?.title === 'function'
      ? props.config.header.title({ route })
      : (props.config?.header?.title || ''))

    const resolvedActions = computed(() => props.config?.header?.actions || [])

    const contextResolver = () => (typeof props.config?.context === 'function'
      ? props.config.context({ route, inject })
      : (props.config?.context || {}))

    return { resolvedTitle, resolvedActions, contextResolver }
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


