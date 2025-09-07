<script setup>
import { computed } from 'vue';
import ToolRunBadge from './ToolRunBadge.vue';

const props = defineProps({
  items: { type: Array, required: true }, // [{ seq, role, message_type, ... }]
  toolsByRunId: { type: Object, required: false, default: () => ({}) }
});

const orderedItems = computed(() => {
  return [...(props.items || [])].sort((a, b) => (a.seq || 0) - (b.seq || 0));
});
</script>

<template>
  <div class="turn-timeline">
    <div class="mb-1">
      <ToolRunBadge
        v-for="(tool, runId) in toolsByRunId"
        :key="runId"
        :toolName="tool.tool_name || 'tool'"
        :status="tool.status || 'started'"
        :toolRunId="runId"
      />
    </div>
    <div v-for="item in orderedItems" :key="item.id || item.seq" class="timeline-item py-1">
      <slot name="item" :item="item" />
    </div>
  </div>
  <div class="mt-1" />
</template>

<style scoped>
.turn-timeline {
  border-left: 2px dashed var(--surface-border);
  padding-left: 0.5rem;
}
.timeline-item {
  position: relative;
}
.timeline-item::before {
  content: '';
  position: absolute;
  left: -11px;
  top: 8px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--surface-500);
}
</style>


