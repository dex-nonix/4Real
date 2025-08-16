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
  <div class="flex mb-4" :class="message.senderId === currentUserId ? 'justify-content-end' : 'justify-content-start'">
    <div class="flex flex-column" style="max-width: 80%;">
      <div class="p-3 surface-200 border-round-xl">
        <div class="flex align-items-center mb-2">
          <i class="pi pi-cog mr-2 text-primary"></i>
          <span class="font-semibold text-sm">{{ toolName }}</span>
          <i :class="getStatusIcon(executionStatus)" class="ml-2"></i>
        </div>
        
        <div class="mb-2">
          <span class="text-xs text-color-secondary">Parameters:</span>
          <pre class="text-xs mt-1 p-2 surface-100 border-round overflow-auto" style="max-height: 100px;">{{ JSON.stringify(toolParams, null, 2) }}</pre>
        </div>
        
        <div v-if="result" class="mb-2">
          <span class="text-xs text-color-secondary">Result:</span>
          <div class="text-sm mt-1 p-2 surface-100 border-round overflow-auto" style="max-height: 150px;">
            {{ typeof result === 'string' ? result : JSON.stringify(result, null, 2) }}
          </div>
        </div>
        
        <div class="text-xs text-color-secondary">
          Status: <span :class="getStatusColor(executionStatus)">{{ executionStatus }}</span>
        </div>
      </div>
      
      <div class="flex align-items-center mt-1 px-2">
        <span class="text-xs text-color-secondary">{{ message.timestamp }}</span>
      </div>
    </div>
  </div>
</template>
