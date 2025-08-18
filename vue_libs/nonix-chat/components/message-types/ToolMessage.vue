<!-- ToolMessage.vue -->
<script setup>
import { computed } from 'vue';

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: [String, Number],
    required: true
  }
});

const toolName = computed(() => props.message.metadata?.toolName || props.message.content_json?.toolName || 'Unknown Tool');
const toolParams = computed(() => props.message.metadata?.toolParams || props.message.content_json?.toolParams || {});
const executionStatus = computed(() => props.message.metadata?.executionStatus || props.message.content_json?.executionStatus || 'pending');
const result = computed(() => props.message.metadata?.result || props.message.content_json?.result || null);
const executedBy = computed(() => props.message.metadata?.executedBy || props.message.content_json?.executedBy || 'unknown');
const executionTime = computed(() => props.message.metadata?.executionTime || props.message.content_json?.executionTime || null);

const getStatusIcon = (status) => {
  switch (status) {
    case 'success': return 'pi pi-check-circle text-success';
    case 'error': return 'pi pi-times-circle text-danger';
    case 'pending': return 'pi pi-clock text-warning';
    default: return 'pi pi-info-circle text-info';
  }
};

const getStatusColor = (status) => {
  switch (status) {
    case 'success': return 'text-success';
    case 'error': return 'text-danger';
    case 'pending': return 'text-warning';
    default: return 'text-info';
  }
};
</script>

<template>
  <!-- Tool message content only - outer styling handled by MessageContainer -->
  
  <div class="mb-2">
    <div class="flex align-items-center gap-2 mb-1">
      <span class="text-xs text-500">Tool:</span>
      <span class="text-sm font-mono font-semibold">{{ toolName }}</span>
      <span class="text-xs text-400">({{ executedBy === 'user' ? 'Executed by User' : 'Executed by AI' }})</span>
    </div>
    <span class="text-xs text-500">Parameters:</span>
    <pre class="text-xs mt-1 p-2 surface-100 border-round overflow-auto" style="max-height: 100px;">{{ JSON.stringify(toolParams, null, 2) }}</pre>
  </div>
  
  <div v-if="result" class="mb-2">
    <span class="text-xs text-500">Result:</span>
    <div class="text-sm mt-1 p-2 surface-100 border-round overflow-auto" style="max-height: 150px;">
      {{ typeof result === 'string' ? result : JSON.stringify(result, null, 2) }}
    </div>
  </div>
  
  <div class="flex align-items-center justify-content-between text-xs text-500">
    <span>Status: <span :class="getStatusColor(executionStatus)">{{ executionStatus }}</span></span>
    <span v-if="executionTime">{{ new Date(executionTime).toLocaleTimeString() }}</span>
  </div>
</template>
