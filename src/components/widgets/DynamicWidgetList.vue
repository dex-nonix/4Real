<template>
  <div :class="listClass">
    <div v-for="(item, idx) in effectiveItems" :key="idx" :class="itemClass(item)">
      <DynamicWidget :widget="item" :ctx="ctx" />
    </div>
  </div>
  </template>

<script>
import DynamicWidget from '@/components/widgets/DynamicWidget.vue'

export default {
  name: 'DynamicWidgetList',
  components: { DynamicWidget },
  props: {
    items: { type: Array, default: () => [] },
    ctx: { type: Object, default: () => ({}) },
    rowClass: { type: String, default: 'grid' },
    gap: { type: String, default: 'gap-3' }
  },
  computed: {
    listClass() {
      return `${this.rowClass} ${this.gap}`.trim()
    }
  },
  methods: {
    itemClass(item) {
      const cls = (item && item.props && item.props.class) || 'col-12'
      return typeof cls === 'string' ? cls : 'col-12'
    },
    computeEffective(items) {
      const out = []
      for (const def of (items || [])) {
        const check = typeof def?.check === 'function' ? def.check : null
        let decision = check ? check(this.ctx) : true
        if (decision === false) continue
        if (decision === true || decision == null) {
          out.push(def)
          continue
        }
        if (Array.isArray(decision)) {
          out.push(...decision)
          continue
        }
        if (typeof decision === 'object') {
          out.push({ ...def, ...decision })
          continue
        }
        out.push(def)
      }
      return out
    }
  },
  computed: {
    effectiveItems() {
      return this.computeEffective(this.items)
    }
  }
}
</script>

<style scoped>
</style>


