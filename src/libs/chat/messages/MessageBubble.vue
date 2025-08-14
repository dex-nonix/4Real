<template>
  <div class="bubble" :class="roleClass">
    <div v-if="role==='tool'">
      <pre class="m-0">{{ pretty(content) }}</pre>
    </div>
    <div v-else>
      <span>{{ content?.text || asText }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  role: { type: String, required: true },
  content: { type: Object, default: () => ({}) },
})

const roleClass = computed(() => ({
  'bubble-user': props.role === 'user',
  'bubble-assistant': props.role === 'assistant',
  'bubble-system': props.role === 'system',
  'bubble-tool': props.role === 'tool',
}))

const asText = computed(() => {
  if (!props.content) return ''
  if (typeof props.content === 'string') return props.content
  if ('text' in props.content) return props.content.text
  try { return JSON.stringify(props.content) } catch { return '' }
})

function pretty(obj) {
  try { return JSON.stringify(obj, null, 2) } catch { return String(obj) }
}
</script>

<style scoped>
.bubble { padding: 0.5rem 0.75rem; border-radius: 0.5rem; margin-bottom: 0.5rem; max-width: 100%; }
.bubble-user { background: var(--primary-100); text-align: right; }
.bubble-assistant { background: var(--surface-200); }
.bubble-system { background: var(--surface-100); font-style: italic; }
.bubble-tool { background: var(--surface-100); font-family: monospace; }
</style>


