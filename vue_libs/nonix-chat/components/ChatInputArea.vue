<script setup>
import { ref, computed, inject, watch } from 'vue';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Menu from 'primevue/menu';
import Badge from 'primevue/badge';
import AvailableToolsDialog from './AvailableToolsDialog.vue';
import ToolExecutionDialog from './ToolExecutionDialog.vue';
import ErrorDialog from './ErrorDialog.vue';
import { VoiceInputButton } from './voice-input-button/index.js';

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

// Consolidated menu items (errors + tools)
const moreMenuItems = computed(() => [
  // Errors section
  {
    label: 'Show Errors',
    icon: 'pi pi-exclamation-triangle',
    command: showErrors,
    badge: props.errors.length > 0 ? props.errors.length : null,
    disabled: props.errors.length === 0
  },

  // Tools section
  {
    label: 'Available Tools',
    icon: 'pi pi-box',
    command: showTools,
    badge: availableToolsLocal.value.length > 0 ? availableToolsLocal.value.length : null,
    disabled: !hasHistory.value || toolsLoading.value
  },

  // Separator
  { separator: true },

  // Additional utilities
  {
    label: 'Clear Input',
    icon: 'pi pi-times',
    command: () => inputText.value = '',
    disabled: !inputText.value?.trim()
  }
]);

// State management
const inputText = ref('');
const showToolsDialog = ref(false);
const availableToolsLocal = ref([]);
const toolsLoading = ref(false);
const selectedTool = ref(null);
const toolExecutionDialogRef = ref(null);

// Badge computation for consolidated notifications
const totalNotifications = computed(() => {
  return props.errors.length + (toolsLoading.value ? 1 : 0);
});

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

// Keyboard event handler for multi-line textarea
const handleKeyDown = (event) => {
  // Send message on Ctrl+Enter or Shift+Enter
  if ((event.ctrlKey || event.shiftKey) && event.key === 'Enter') {
    event.preventDefault();
    if (inputText.value?.trim() && !isStreaming.value) {
      buttonAction.value();
    }
  }
  // Allow default behavior for Enter (new line) and other keys
};

// Voice input event handlers
const handleVoiceText = ({ text, confidence, isFinal }) => {
  if (isFinal && text.trim()) {
    // Append to current input or replace if empty
    if (inputText.value) {
      inputText.value += ' ' + text.trim();
    } else {
      inputText.value = text.trim();
    }
  }
};

const handleRecordingError = ({ error, code }) => {
  console.error('Voice recording error:', error, code);
  emit('error', {
    message: 'Voice input error',
    details: { error, code }
  });
};

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
  <div class="flex align-items-end px-2 py-1 pb-2 surface-section gap-2">
    <!-- Voice Input Button -->
    <div class="mb-2 ml-1">
      <VoiceInputButton
        :disabled="!hasHistory || isStreaming"
        @text="handleVoiceText"
        @recording-error="handleRecordingError"
        size="small"
      />
    </div>

    <!-- Input Field -->
    <span class="p-input-icon-right flex-1 relative">
      <IconField>
        <Textarea
          v-model="inputText"
          placeholder="Type a message..."
          class="w-full compact-textarea"
          :autoResize="true"
          rows="1"
          :maxlength="5000"
          @keydown="handleKeyDown"
          :disabled="!hasHistory || isStreaming"
        />
        <InputIcon :class="buttonIcon + ' absolute bottom-0 right-0 mb-1 mr-1'" @click="buttonAction" />
      </IconField>
    </span>

    <!-- Options Button -->
    <div class="relative mb-2 mr-1">
      <Button
        icon="pi pi-ellipsis-h"
        text
        rounded
        severity="secondary"
        :disabled="!hasHistory"
        style="width: 24px; height: 24px;"
        @click="toggleMoreMenu"
        aria-haspopup="true"
        aria-controls="more_menu"
      />
      <Badge v-if="totalNotifications > 0" :value="totalNotifications" severity="danger"
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
/* Make textarea with comfortable padding for send button */
.compact-textarea {
  padding: 0.5rem 2.75rem 0.5rem 0.5rem !important;
  min-height: 1.75rem !important;
  font-size: 0.875rem !important;
  line-height: 1.25 !important;
  border-radius: 4px !important;
}

/* Position send icon fixed at bottom of textarea */
:deep(.p-input-icon) {
  position: absolute !important;
  bottom: 0.375rem !important;
  right: 0.5rem !important;
  top: auto !important;
  transform: none !important;
  width: 1.25rem !important;
  height: 1.25rem !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer !important;
  border-radius: 50% !important;
  transition: all 0.2s ease !important;
}

.compact-textarea :deep(.p-input-icon:hover) {
  background-color: var(--surface-200);
}
</style>
