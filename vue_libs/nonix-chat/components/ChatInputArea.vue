<script setup>
import { ref, computed, inject, watch } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Menu from 'primevue/menu';
import Badge from 'primevue/badge';
import AvailableToolsDialog from './AvailableToolsDialog.vue';
import ToolExecutionDialog from './ToolExecutionDialog.vue';
import ErrorDialog from './ErrorDialog.vue';

const props = defineProps({
  // Session context
  sessionId: { type: [String, Number, null], required: true },
  historyId: { type: [String, Number, null], required: false, default: null },
  selectedSession: { type: Object, required: false, default: null },

  // Error display
  errors: { type: Array, default: () => [] },

  // Available tools from parent
  availableTools: { type: Array, default: () => [] },

  // Streaming state
  streamingStatus: { type: Map, required: true },
  streamingMessages: { type: Map, required: true },

  // Messages for optimistic updates
  messages: { type: Array, required: true }
});

const emit = defineEmits(['sendMessage', 'error']);

// Service injection
const chatService = inject('chat-service');

// Error management
const showErrorDialog = ref(false);
const moreMenu = ref();

// Show error dialog
const showErrors = () => {
  showErrorDialog.value = true;
};

// Toggle more menu
const toggleMoreMenu = (event) => {
  moreMenu.value.toggle(event);
};

// Menu items
const moreMenuItems = computed(() => [
  {
    label: 'Show Errors',
    icon: 'pi pi-exclamation-triangle',
    command: showErrors,
    badge: props.errors.length > 0 ? props.errors.length : null
  }
]);

// State management
const inputText = ref('');
const showToolsDialog = ref(false);
const availableToolsLocal = ref([]);
const toolsLoading = ref(false);
const selectedTool = ref(null);
const toolExecutionDialogRef = ref(null);

// Session-specific input text storage
const sessionInputTexts = ref(new Map());

// Tools state
const showTools = async () => {
  try {
    toolsLoading.value = true;
    showToolsDialog.value = true;

    // Load tools for the current persona
    if (props.selectedSession?.persona_id && chatService) {
      const toolsData = await chatService.personaTools(props.selectedSession.persona_id);

      // Backend returns {data: Array} - extract the actual tools array
      let toolsArray = [];
      if (toolsData && toolsData.data && Array.isArray(toolsData.data)) {
        toolsArray = toolsData.data;
      } else if (Array.isArray(toolsData)) {
        toolsArray = toolsData;
      }

      availableToolsLocal.value = toolsArray;
    } else {
      availableToolsLocal.value = [];
    }
  } catch (error) {
    console.error('Failed to load tools:', error);
    availableToolsLocal.value = [];
  } finally {
    toolsLoading.value = false;
  }
};

// Select tool and show parameter form
const selectTool = (toolData) => {
  selectedTool.value = toolData;
  if (toolExecutionDialogRef.value) {
    toolExecutionDialogRef.value.openDialog(toolData);
  }
};

// Execute tool with form data
const executeToolWithForm = async (formData) => {
  if (!selectedTool.value || !props.selectedSession?.persona_id || !props.historyId || !chatService) {
    console.error('Cannot execute tool: Missing required data');
    return;
  }

  // Extract the actual form data from DynamicForm's submit event
  const args = formData.__full || formData.args || {};

  try {
    await chatService.sendMessage(
      props.selectedSession.id,
      props.historyId,
      {
        message_type: 'tool_call',
        content: {
          tool: selectedTool.value.name,
          args: args
        }
      }
    );

    // Backend returns: { tool_call_message_id, tool_result_message_id, status, result }
    // WebSocket events will update the UI with real database messages

    // Close tool form immediately on success
    showToolsDialog.value = false;
    selectedTool.value = null;

    // WebSocket events will automatically update the UI with real tool messages

  } catch (error) {
    console.error('Tool execution failed:', error);

    // ✅ FIXED: Don't create dummy error messages - show error in UI differently
    // For now, just log the error. Later we can add a proper error toast/notification
    // WebSocket events should handle any backend-generated error messages

    // Close tool form on error too
    showToolsDialog.value = false;
    selectedTool.value = null;
  }
};

// Send message
const onSend = async () => {
  if (!inputText.value?.trim() || !props.historyId || !chatService) return;

  try {
    // Clear error states when sending new message
    props.streamingStatus.forEach((status, messageId) => {
      if (status === 'error') {
        props.streamingStatus.set(messageId, 'complete');
      }
    });

    // Clear streaming messages
    props.streamingMessages.clear();

    // Send proper message payload (type=text per base chat message)
    const messageData = {
      historyId: props.historyId,
      message_type: 'user',
      content: {
        text: inputText.value.trim()
      }
    };

    // Save current input text for this session before clearing
    if (props.selectedSession?.id) {
      sessionInputTexts.value.set(props.selectedSession.id, inputText.value);
    }

    // Emit event for parent component
    emit('sendMessage', messageData);

    // Clear input after sending
    inputText.value = '';

    // Optimistic UI: append the user message locally instead of reloading full list
    try {
      const tempId = `temp-${Date.now()}`;
      const userMessage = {
        id: tempId,
        message_type: 'user',
        role: 'user',
        content_json: { text: messageData.content.text },
        status: 'sending',
        created_at: new Date().toISOString()
      };
      props.messages.push(userMessage);
    } catch (e) {
      console.error('Failed to append optimistic user message:', e);
    }
  } catch (error) {
    console.error('Failed to send message:', error);
    emit('error', {
      message: 'Failed to send message',
      details: error
    });
  }
};

// Stop streaming functionality
const onStop = async () => {
  if (!props.selectedSession?.id || !chatService) return;
  try {
    const streamingMsg = props.messages.find(m => m.role === 'assistant' && m.status === 'streaming');
    let response;
    if (streamingMsg && props.historyId) response = await chatService.cancelMessage(props.selectedSession.id, props.historyId, streamingMsg.id);
    else return;
    if (response && response.cancelled) {
      props.streamingStatus.forEach((status, messageId) => {
        if (status === 'streaming') props.streamingStatus.set(messageId, 'complete');
      });
      props.streamingMessages.clear();
      props.messages.forEach(msg => {
        if (msg.status === 'streaming') {
          msg.status = 'complete';
        }
      });
    }
  } catch (error) {
    emit('error', {
      message: 'Failed to stop streaming',
      details: error
    });
  }
};

// Retry functionality
const onRetry = async () => {
  if (!props.selectedSession?.id || !chatService) return;
  try {
    const response = await chatService.retryLastMessage(props.selectedSession.id);
    if (response?.status === 'processing') {
      props.streamingStatus.forEach((status, messageId) => {
        if (status === 'error') props.streamingStatus.set(messageId, 'complete');
      });
      props.streamingMessages.clear();
      props.messages.forEach(msg => {
        if (msg.status === 'error') {
          msg.status = 'complete';
        }
      });
    }
  } catch (error) {
    emit('error', {
      message: 'Failed to retry message',
      details: error
    });
  }
};

// Computed values
const hasHistory = computed(() => !!props.historyId);

// Button state management
const isStreaming = computed(() => {
  try {
    if (!(props.streamingStatus instanceof Map)) return false;
    return Array.from(props.streamingStatus.values()).some(status => status === 'streaming');
  } catch { return false; }
});
const hasErrors = computed(() => {
  try {
    if (!(props.streamingStatus instanceof Map)) return false;
    return Array.from(props.streamingStatus.values()).some(status => status === 'error');
  } catch { return false; }
});
const canRetry = computed(() => hasErrors.value && !isStreaming.value);

const buttonIcon = computed(() => {
  if (isStreaming.value) return 'pi pi-stop';
  if (canRetry.value) return 'pi pi-refresh';
  return 'pi pi-send';
});
const buttonAction = computed(() => {
  if (isStreaming.value) return onStop;
  if (canRetry.value) return onRetry;
  return onSend;
});

// Watch for session changes
watch(() => props.selectedSession, (newSession, oldSession) => {
  if (newSession) {
    // Save input text for previous session if it exists
    if (oldSession && oldSession.id) {
      sessionInputTexts.value.set(oldSession.id, inputText.value);
    }

    // Load input text for new session
    if (newSession.id) {
      inputText.value = sessionInputTexts.value.get(newSession.id) || '';
    }
  }
}, { immediate: true });

// Expose methods for parent component
defineExpose({
  // Expose streaming methods if needed by parent
});
</script>

<template>
  <div class="input-area">
    <!-- Tools Button -->
    <Button icon="pi pi-box" text rounded severity="secondary" @click="showTools"
      v-tooltip.bottom="'Available Tools'" :disabled="!hasHistory" />

    <!-- Input Field -->
    <span class="p-input-icon-right flex-grow-1 mx-1">
      <IconField>
        <InputText v-model="inputText" placeholder="Type a message..." class="w-full" @keyup.enter="buttonAction"
          :disabled="!hasHistory || isStreaming" />
        <InputIcon :class="buttonIcon" @click="buttonAction" />
      </IconField>
    </span>

    <!-- Options Button -->
    <div class="relative">
      <Button icon="pi pi-ellipsis-h" text rounded severity="secondary" :disabled="!hasHistory"
        @click="toggleMoreMenu" aria-haspopup="true" aria-controls="more_menu" />
      <Badge v-if="props.errors.length > 0" :value="props.errors.length" severity="danger"
        class="absolute top-0 right-0 transform translate-x-1/2 -translate-y-1/2" />
    </div>

    <!-- More Menu -->
    <Menu ref="moreMenu" id="more_menu" :model="moreMenuItems" :popup="true" />
    <!-- Tools Dialog -->
    <AvailableToolsDialog :visible="showToolsDialog" :tools="availableToolsLocal"
      @update:visible="showToolsDialog = $event" @tool-selected="selectTool" />

    <!-- Tool Execution Dialog -->
    <ToolExecutionDialog ref="toolExecutionDialogRef" :selected-tool="selectedTool"
      @execute-tool="executeToolWithForm" />
  </div>

  <!-- Error Dialog -->
  <ErrorDialog :visible="showErrorDialog" :errors="props.errors" @update:visible="showErrorDialog = $event" />
</template>

<style scoped>
/* Input area - compact fixed position */
.input-area {
  display: flex;
  align-items: center;
  padding: 0.5rem;

  background: var(--surface-section);
}

/* Button layout and spacing */
.input-area .p-button {
  flex-shrink: 0;
}

/* Retry button styling */
.input-area .p-button[severity="warning"] {
  border-color: var(--warning-color);
  color: var(--warning-color);
}

/* Stop button styling */
.input-area .p-button[severity="danger"] {
  border-color: var(--danger-color);
  color: var(--danger-color);
}

/* Send button styling */
.input-area .p-button[severity="primary"] {
  border-color: var(--primary-color);
  color: var(--primary-color);
}
</style>
