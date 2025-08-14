<template>
  <div class="persona-tools-viewer">
    <h3 class="mt-0">Available Tools</h3>
    <div v-if="loading" class="text-sm text-gray-600">Loading tools...</div>
    <ul v-else class="list-none p-0 m-0 flex flex-column gap-2">
      <li v-for="t in tools" :key="t" class="flex align-items-center gap-2">
        <i class="pi pi-wrench"></i>
        <span class="font-mono text-sm">{{ t }}</span>
      </li>
      <li v-if="!tools.length" class="text-sm text-gray-600">No tools available</li>
    </ul>
  </div>
  </template>

<script>
export default {
  name: 'PersonaToolsViewer',
  props: {
    personaId: { type: [String, Number], required: true }
  },
  data() {
    return { tools: [], loading: false }
  },
  methods: {
    async load() {
      this.loading = true
      try {
        const { API_BASE_URL } = await import('@/config.js')
        const res = await fetch(`${API_BASE_URL}/chat/personas/${this.personaId}/tools`)
        const data = await res.json()
        this.tools = Array.isArray(data?.data) ? data.data : []
      } catch (e) {
        this.tools = []
      } finally {
        this.loading = false
      }
    }
  },
  mounted() { this.load() },
  watch: {
    personaId() { this.load() }
  }
}
</script>

<style scoped>
</style>


