<template>
  <div class="tool-call surface-100 p-2 border-round">
    <div class="text-600 mb-1">Tool Result</div>
    <pre class="m-0">{{ pretty(content) }}</pre>
  </div>
</template>

<script setup>
const props = defineProps({ content: { type: Object, default: () => ({}) } })

function pretty(obj) {
  try { return JSON.stringify(obj, null, 2) } catch { return String(obj) }
}
</script>

<style scoped>
.tool-call { width: 100%; }
</style>


