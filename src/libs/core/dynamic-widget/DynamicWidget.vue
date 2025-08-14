<template>
  <component :is="resolved.component" v-bind="resolved.props" />
  </template>

<script>
import DynamicWidgetManager from '@/libs/core/widget-manager/DynamicWidgetManager.js'

export default {
  name: 'DynamicWidget',
  props: {
    widget: { type: [String, Object], required: true },
    props: { type: [Object, Function], default: () => ({}) },
    context: { type: Object, default: () => ({}) }
  },
  data() {
    return {
      manager: new DynamicWidgetManager()
    }
  },
  computed: {
    resolved() {
      const def = typeof this.widget === 'string' ? { type: this.widget } : (this.widget || {})
      const type = def.type
      const comp = def.component
      const userProps = typeof (def.props ?? this.props) === 'function'
        ? (def.props ?? this.props)(this.context)
        : { ...(def.props || {}), ...(this.props || {}) }
      if (comp) return { component: comp, props: userProps }
      return this.manager.getWidget(type, userProps)
    }
  }
}
</script>

<style scoped>
</style>


