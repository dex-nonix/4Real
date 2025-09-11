<template>
  <div class="dynamic-page">
    <NxPage :title="resolvedTitle" :back="Boolean(config?.header?.back)" :actions="resolvedActions"/>
    <NxDynamicWidgetList
        :items="config?.widgets || []"
        :context="contextResolver"
        :rowClass="config?.layout?.rowClass || 'grid'"
        :gap="config?.layout?.gap || 'gap-3'"
    />
  </div>
</template>

<script>
import NxDynamicWidgetList from '@nonix-dynamic/widget/components/NxDynamicWidgetList.vue'
import NxPage from '@nonix/page/NxPage.vue'
import {useRoute} from 'vue-router'
import {computed, inject} from 'vue'
import NxPageManager from '@nonix/widget-manager/NxPageManager.js'

const NxDynamicPage = {
  name: 'NxDynamicPage',
  components: {NxDynamicWidgetList, NxPage},

  setup() {
    const route = useRoute()

    // Resolve page config from route meta using the existing function
    const config = computed(() => resolveRoutePageConfig(route))

    const resolvedTitle = computed(() => typeof config.value?.header?.title === 'function'
        ? config.value.header.title({route})
        : (config.value?.header?.title || ''))

    const resolvedActions = computed(() => config.value?.header?.actions || [])

    const contextResolver = () => (typeof config.value?.context === 'function'
        ? config.value.context({route, inject})
        : (config.value.context || {}))

    return {config, resolvedTitle, resolvedActions, contextResolver}
  }
}

// Static helper on component object
NxDynamicPage.createRoute = function (path, page, meta = {}) {
  return {path, component: NxDynamicPage, meta: {page, ...meta}}
}

// Route meta resolver: returns a config object
export function resolveRoutePageConfig(route) {
  const src = route?.meta?.page
  if (typeof src === 'function') return src({route, inject})
  if (typeof src === 'string') {
    const {component} = NxPageManager.getWidget(src)
    return component
  }
  return src || {header: {title: ''}, widgets: []}
}

export default NxDynamicPage
</script>

<style scoped>
</style>


