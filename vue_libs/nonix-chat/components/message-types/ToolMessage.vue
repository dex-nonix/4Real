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

// Declare emits for Vue 3 event handling
const emit = defineEmits(['deleteMessage']);

const toolName = computed(() => props.message.metadata?.tool_name || props.message.content_json?.tool_name || 'Unknown Tool');
const toolParams = computed(() => props.message.metadata?.tool_args || props.message.content_json?.tool_args || {});
const executionStatus = computed(() => props.message.metadata?.execution_status || props.message.content_json?.execution_status || 'pending');
const result = computed(() => props.message.metadata?.result || props.message.content_json?.result || null);
const executedBy = computed(() => props.message.metadata?.executed_by || props.message.content_json?.executed_by || 'unknown');
const executionTime = computed(() => props.message.metadata?.execution_time || props.message.content_json?.execution_time || null);

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
