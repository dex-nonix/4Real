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

// Our strict structure: tool fields are available directly on the message object (no fallbacks)
const toolName = computed(() => props.message.tool_name || 'Unknown Tool');
const toolParams = computed(() => props.message.tool_args || {});
const executionStatus = computed(() => props.message.execution_status || 'pending');
const result = computed(() => props.message.result || null);
const executedBy = computed(() => props.message.executed_by || 'unknown');
const executionTime = computed(() => props.message.execution_time || null);

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

// Status helper functions
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

  <!-- Message Content -->
  <div class="flex align-items-start justify-content-start">
    <div class="flex-grow-1">
      <div class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">
        <div class="mb-2">
          <div class="flex align-items-center gap-2 mb-1">
            <i class="pi pi-wrench text-primary text-sm"></i>
            <span class="text-sm font-semibold">{{ toolName }}</span>
            <span class="text-xs text-500">({{ executedBy === 'user' ? 'Executed by User' : 'Executed by AI' }})</span>
          </div>

          <div class="text-xs text-600 mb-1">
            <strong>Parameters:</strong> {{ formattedParams }}
          </div>

          <div v-if="extractedResult" class="text-xs text-600">
            <strong>Result:</strong>
            <div class="mt-1 ml-2 text-sm">
              <!-- Generic formatted display for objects -->
              <div v-if="isSimpleObject(extractedResult)" class="flex flex-column gap-1">
                <div v-for="(value, key) in extractedResult" :key="key" class="flex justify-content-between align-items-center">
                  <span class="font-medium text-700 text-capitalize">
                    {{ key.replace(/_/g, ' ') }}:
                  </span>
                  <span class="font-normal">
                    {{ formatValue(value, key) }}
                  </span>
                </div>
              </div>
              <!-- Display arrays in a compact format -->
              <div v-else-if="Array.isArray(extractedResult)">
                <div class="font-medium text-700 mb-1">
                  {{ extractedResult.length }} item{{ extractedResult.length !== 1 ? 's' : '' }}:
                </div>
                <div v-for="(item, index) in extractedResult" :key="index" class="ml-2 mb-1">
                  <span class="text-600">{{ index + 1 }}.</span>
                  <span class="ml-1">
                    {{ typeof item === 'object' ? JSON.stringify(item) : item }}
                  </span>
                </div>
              </div>
              <!-- Fallback for complex objects or raw data -->
              <div v-else class="font-mono text-xs overflow-auto" style="max-height: 150px;">
                {{ typeof extractedResult === 'string' ? extractedResult : JSON.stringify(extractedResult, null, 2) }}
              </div>
            </div>
          </div>
        </div>

        <div class="flex align-items-center justify-content-between text-xs text-500 mt-2">
          <span>Status: <span :class="getStatusColor(executionStatus)">{{ executionStatus }}</span></span>
          <span v-if="executionTime">{{ new Date(executionTime).toLocaleTimeString() }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
