<template>
  <div :class="listClass">
    <div v-for="(item, idx) in effectiveItems" :key="idx" :class="itemClass(item)">
      <DynamicWidget :widget="item" :context="resolvedContext" />
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
    context: { type: [Object, Function], default: () => ({}) },
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
    async resolveContext() {
      try {
        if (typeof this.context === 'function') {
          const out = this.context()
          return typeof out?.then === 'function' ? await out : out
        }
        return this.context || {}
      } catch (e) { return {} }
    },
    async computeEffective(items) {
      const ctx = await this.resolveContext()
      const out = []
      for (const def of (items || [])) {
        const check = typeof def?.check === 'function' ? def.check : null
        const setup = typeof def?.setup === 'function' ? def.setup : null
        // setup phase
        let decision = true
        if (setup) {
          let r = setup(ctx)
          r = (r && typeof r.then === 'function') ? await r : r
          if (r === false) continue
          if (Array.isArray(r)) { out.push(...r); continue }
          if (r && typeof r === 'object') {
            Object.assign(def, r)
          }
        }
        // check phase
        decision = check ? check(ctx) : true
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
      this._lastResolvedContext = ctx
      return out
    }
  },
  computed: {
    effectiveItems() {
      return this._eff // computed async via created/mounted
    },
    resolvedContext() {
      return this._lastResolvedContext || (typeof this.context === 'object' ? this.context : {})
    }
  },
  data() {
    return { _eff: [], _lastResolvedContext: null }
  },
  async created() {
    this._eff = await this.computeEffective(this.items)
  },
  watch: {
    items: {
      deep: true,
      async handler() { this._eff = await this.computeEffective(this.items) }
    },
    context: {
      deep: false,
      async handler() { this._eff = await this.computeEffective(this.items) }
    }
  }
}
</script>

<style scoped>
</style>


