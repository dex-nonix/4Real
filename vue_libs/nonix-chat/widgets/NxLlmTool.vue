<template>
  <div v-if="mode !== 'display'">
    <AutoComplete
      :modelValue="inputValue"
      @update:modelValue="onAutoUpdate"
      :suggestions="filtered"
      @complete="onComplete"
      :placeholder="placeholder || 'Select or type a tool'"
      :dropdown="true"
      :optionLabel="'name'"
      class="w-full"
    />
  </div>
  <span v-else :title="description" class="text-sm font-mono">{{ modelValue }}</span>
</template>

<script>
import AutoComplete from 'primevue/autocomplete'

export default {
  name: 'NxLlmTool',
  components: { AutoComplete },
  props: {
    modelValue: { type: String, default: '' },
    mode: { type: String, default: 'edit' },
    allowWildcards: { type: Boolean, default: true },
    placeholder: { type: String, default: '' },
    fetchUrl: { type: String, default: '/chat/tools/registry' }
  },
  emits: ['update:modelValue', 'change'],
  data() {
    return {
      inputValue: this.modelValue || '',
      items: [],
      filtered: [],
      byName: {}
    }
  },
  computed: {
    description() {
      return this.byName[this.modelValue || ''] || ''
    }
  },
  watch: {
    modelValue(v) {
      this.inputValue = v || ''
    }
  },
  mounted() {
    this.load()
  },
  methods: {
    async load() {
      try {
        const res = await fetch(this.fetchUrl)
        const json = await res.json()
        const list = (json && (json.data || json)) || []
        this.items = Array.isArray(list) ? list : []
        const map = {}
        for (const it of this.items) {
          if (it && it.name) map[it.name] = it.description || ''
        }
        this.byName = map
      } catch (e) {
        this.items = []
        this.byName = {}
      }
    },
    onComplete(e) {
      const q = (e && e.query ? e.query : '').toLowerCase()
      if (!q) {
        this.filtered = this.items
        return
      }
      this.filtered = this.items.filter(it => {
        const n = (it.name || '').toLowerCase()
        const d = (it.description || '').toLowerCase()
        return n.includes(q) || d.includes(q)
      })
    },
    onSelectName(name) {
      this.inputValue = name
      this.$emit('update:modelValue', name)
      this.$emit('change', name)
    },
    onAutoUpdate(val) {
      if (val && typeof val === 'object' && val.name) {
        this.onSelectName(val.name)
        return
      }
      const v = typeof val === 'string' ? val : ''
      this.inputValue = v
      this.$emit('update:modelValue', v)
      this.$emit('change', v)
    }
  }
}
</script>

<style scoped>
</style>


