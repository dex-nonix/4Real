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

const toolName = computed(() => props.message.metadata?.toolName || 'Unknown Tool');
const toolParams = computed(() => props.message.metadata?.toolParams || {});
const executionStatus = computed(() => props.message.metadata?.executionStatus || 'pending');
const result = computed(() => props.message.metadata?.result || null);

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
    <span class="text-xs text-500">Parameters:</span>
    <pre class="text-xs mt-1 p-2 surface-100 border-round overflow-auto" style="max-height: 100px;">{{ JSON.stringify(toolParams, null, 2) }}</pre>
  </div>
  
  <div v-if="result" class="mb-2">
    <span class="text-xs text-500">Result:</span>
    <div class="text-sm mt-1 p-2 surface-100 border-round overflow-auto" style="max-height: 150px;">
      {{ typeof result === 'string' ? result : JSON.stringify(result, null, 2) }}
    </div>
  </div>
  
  <div class="text-xs text-500">
    Status: <span :class="getStatusColor(executionStatus)">{{ executionStatus }}</span>
  </div>
</template>
