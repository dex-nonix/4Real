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

// Our strict structure: tool fields are available directly on the message object
const toolName = computed(() => props.message.tool_name || props.message.content_json?.tool_name || 'Unknown Tool');
const toolParams = computed(() => props.message.tool_args || props.message.content_json?.tool_args || {});
const executionStatus = computed(() => props.message.execution_status || props.message.content_json?.execution_status || 'pending');
const result = computed(() => props.message.result || props.message.content_json?.result || null);
const executedBy = computed(() => props.message.executed_by || props.message.content_json?.executed_by || 'unknown');
const executionTime = computed(() => props.message.execution_time || props.message.content_json?.execution_time || null);

// Format parameters compactly
const formattedParams = computed(() => {
  if (!toolParams.value || Object.keys(toolParams.value).length === 0) {
    return 'No parameters';
  }

  return Object.entries(toolParams.value)
    .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
    .join(', ');
});

// Extract data from result - our app has ONE consistent structure
const extractedResult = computed(() => {
  if (!result.value) return null;

  // Tool execution structure: {"status": "success", "result": {"success": true, "data": <actual_data>}}
  // So result.result.data is ALWAYS the meaningful data to display
  const toolResult = result.value.result;
  return toolResult?.data;
});

// Generic formatter for any object data
const formatValue = (value, key) => {
  if (value === null || value === undefined) return 'null';

  // Format dates nicely
  if (key.toLowerCase().includes('date') || key.toLowerCase().includes('time') || key.toLowerCase().includes('created') || key.toLowerCase().includes('updated')) {
    try {
      return new Date(value).toLocaleString();
    } catch (e) {
      // Not a valid date, continue with normal formatting
    }
  }

  // Format boolean values nicely
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }

  // Format numbers
  if (typeof value === 'number') {
    return value.toLocaleString();
  }

  return value;
};

// Check if result is a simple object (not array or complex nested)
const isSimpleObject = (obj) => {
  return obj && typeof obj === 'object' && !Array.isArray(obj) &&
         Object.keys(obj).length > 0 && Object.keys(obj).length <= 10;
};

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
    <div class="text-xs mt-1 p-2 surface-100 border-round">
      {{ formattedParams }}
    </div>
  </div>

  <div v-if="extractedResult" class="mb-2">
    <span class="text-xs text-500">Result:</span>
    <div class="text-sm mt-1 p-2 surface-100 border-round overflow-auto" style="max-height: 200px;">
      <!-- Generic formatted display for objects -->
      <div v-if="isSimpleObject(extractedResult)" style="display: flex; flex-direction: column; gap: 8px;">
        <!-- Display each property in a nice format -->
        <div v-for="(value, key) in extractedResult" :key="key" style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 500; color: var(--text-color-secondary); text-transform: capitalize; font-size: 0.875rem;">
            {{ key.replace(/_/g, ' ') }}:
          </span>
          <span style="font-weight: 600; color: var(--text-color); font-size: 0.875rem;">
            {{ formatValue(value, key) }}
          </span>
        </div>
      </div>
      <!-- Display arrays in a compact format -->
      <div v-else-if="Array.isArray(extractedResult)" style="font-size: 0.875rem;">
        <div style="font-weight: 500; color: var(--text-color-secondary); margin-bottom: 4px;">
          {{ extractedResult.length }} item{{ extractedResult.length !== 1 ? 's' : '' }}:
        </div>
        <div v-for="(item, index) in extractedResult" :key="index" style="margin-left: 8px; margin-bottom: 4px;">
          <span style="color: var(--text-color-secondary);">{{ index + 1 }}.</span>
          <span style="margin-left: 4px;">
            {{ typeof item === 'object' ? JSON.stringify(item) : item }}
          </span>
        </div>
      </div>
      <!-- Fallback for complex objects or raw data -->
      <div v-else class="font-mono text-xs">
        {{ typeof extractedResult === 'string' ? extractedResult : JSON.stringify(extractedResult, null, 2) }}
      </div>
    </div>
  </div>
  
  <div class="flex align-items-center justify-content-between text-xs text-500">
    <span>Status: <span :class="getStatusColor(executionStatus)">{{ executionStatus }}</span></span>
    <span v-if="executionTime">{{ new Date(executionTime).toLocaleTimeString() }}</span>
  </div>
</template>
