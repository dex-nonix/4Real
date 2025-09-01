<script setup>
import { ref, computed, onMounted, onUnmounted, inject, watch } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Menu from 'primevue/menu';
import Badge from 'primevue/badge';
import ErrorDialog from './ErrorDialog.vue';
import chatMessageTypeManager from './ChatMessageTypeManager.js';
import TextMessage from './message-types/TextMessage.vue';
import SystemMessage from './message-types/SystemMessage.vue';
import ToolMessage from './message-types/ToolMessage.vue';
import UserMessage from './message-types/UserMessage.vue';
import { IncomingMessageContainer, OutgoingMessageContainer } from './message-types/index.js';
import StreamingMessage from './message-types/StreamingMessage.vue';
import AvailableToolsDialog from './AvailableToolsDialog.vue';
import ToolExecutionDialog from './ToolExecutionDialog.vue';

const props = defineProps({
  sessionId: { type: [String, Number, null], required: true },
  historyId: { type: [String, Number, null], required: false, default: null },
  currentUserId: { type: [String, Number], required: true, default: 'user-self' },
  selectedSession: { type: Object, required: false, default: null },
  availableTools: { type: Array, default: () => [] },
  errors: { type: Array, required: false, default: () => [] }
});

const emit = defineEmits(['sendMessage', 'regenerateResponse', 'showTools', 'deleteMessage', 'error']);

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

// State management - session-specific
const messages = ref([]);
const inputText = ref('');
const loading = ref(false);

// WebSocket Real-time State
const llmStatus = ref(null);
const toolStatus = ref(null);
const realTimeMessages = ref([]);

// NEW: Streaming message state management
const streamingMessages = ref(new Map()); // message_id -> { content, status, metadata }
const streamingStatus = ref(new Map());   // message_id -> 'streaming' | 'complete' | 'error'

// Session-specific input text storage
const sessionInputTexts = ref(new Map());

// Tools state
const showToolsDialog = ref(false);
const availableTools = ref([]);
const toolsLoading = ref(false);
const selectedTool = ref(null);
const toolExecutionDialogRef = ref(null);

// Track active WebSocket unsubscribers to avoid duplicate handlers
const wsUnsubs = ref([]);

const cleanupWsListeners = () => {
  try {
    if (Array.isArray(wsUnsubs.value)) {
      wsUnsubs.value.forEach(unsub => {
        try { typeof unsub === 'function' && unsub(); } catch (_) {}
      });
    }
  } finally {
    wsUnsubs.value = [];
  }
};

// Register all message types with the manager
onMounted(() => {
  chatMessageTypeManager.clearMessageTypes();
  chatMessageTypeManager.registerMessageType('user', UserMessage);
  chatMessageTypeManager.registerMessageType('assistant', StreamingMessage);
  chatMessageTypeManager.registerMessageType('system', SystemMessage);
  chatMessageTypeManager.registerMessageType('tool_result', ToolMessage);
});

// Cleanup WebSocket resources on unmount
onUnmounted(() => {
  if (props.selectedSession && props.historyId) {
    const room = `chat/${props.selectedSession.id}/${props.historyId}`;
    chatService.leaveRoom(room);
  }
  cleanupWsListeners();
});

// WebSocket Event Handlers
const handleLLMStatus = (data) => {
  console.log('🎯 LLM Status event received:', data);
  const { stage, message, timestamp } = data;
  console.log('LLM Status:', stage, message, timestamp);
  // Update UI state based on LLM stage
  updateLLMStatus(stage, message);
};

const handleToolStatus = (data) => {
  console.log('🎯 Tool Status event received:', data);
  const { tool_name, status, result, error, timestamp } = data;
  console.log('Tool Status:', tool_name, status, result, error);
  // Update UI state based on LLM stage
  updateToolStatus(tool_name, status, result, error);
};

const handleMessageReceived = (data) => {
  console.log('🎯 Message Received event:', data);
  const { message_id, role, content, timestamp, message_type: incomingType, status } = data;
  console.log('Message Received:', message_id, role, content);

  // Upsert incoming message into messages array to avoid duplicates
  try {
    const derivedType = incomingType
      || (role === 'assistant' ? 'assistant'
          : role === 'user' ? 'user'
          : role === 'system' ? 'system'
          : 'tool_result');
    const incoming = {
      id: message_id,
      role: role,
      message_type: derivedType,
      content_json: content,
      status: status || 'complete',
      created_at: timestamp || new Date().toISOString()
    };

    // If this is the user's own message, replace the latest optimistic 'sending' entry
    if (role === 'user') {
      for (let i = messages.value.length - 1; i >= 0; i--) {
        const m = messages.value[i];
        if (m && m.role === 'user' && m.status === 'sending') {
          messages.value[i] = Object.assign({}, m, incoming);
          return;
        }
      }
    }

    const idx = messages.value.findIndex(m => String(m.id) === String(message_id));
    if (idx !== -1) {
      // Update existing message (replace temporary optimistic message)
      messages.value[idx] = Object.assign({}, messages.value[idx], incoming);
    } else {
      messages.value.push(incoming);
    }
  } catch (e) {
    console.error('Failed to upsert incoming message:', e);
  }
};

const handleMessageProcessed = (data) => {
  console.log('🎯 Message Processed event:', data);
  const { message_id, status, timestamp } = data;
  console.log('Message Processed:', message_id, status);
  // Update message status
  updateMessageStatus(message_id, status);
};

// Streaming event handlers
const handleAssistantStarted = (data) => {
  console.log('🎯 Assistant Message Started event:', data);
  // Create empty assistant message
  const { message_id, status, metadata } = data;
  console.log('Creating streaming message with ID:', message_id);
  
  const existingIndex = messages.value.findIndex(m => m.id === message_id);
  if (existingIndex !== -1) {
    messages.value[existingIndex].status = 'streaming';
  } else {
    const assistantMessage = {
      id: message_id,
      role: 'assistant',
      message_type: 'assistant',
      content_json: { text: '' },
      status: 'streaming',
      created_at: new Date().toISOString()
    };
    messages.value.push(assistantMessage);
  }
  console.log('Added streaming message to UI. Total messages:', messages.value.length);
  
  // Track streaming state
  streamingMessages.value.set(message_id, { content: '', status: 'streaming', metadata });
  streamingStatus.value.set(message_id, 'streaming');
};

const handleAssistantChunk = (data) => {
  console.log('🎯 Assistant Message Chunk event:', data);
  // Find existing assistant message and append chunk
  const { message_id, chunk, metadata, is_final } = data;
  console.log('Looking for message with ID:', message_id, 'in', messages.value.length, 'messages');
  
  const messageIndex = messages.value.findIndex(m => m.id === message_id);
  console.log('Found message at index:', messageIndex);
  
  if (messageIndex !== -1) {
    const currentText = messages.value[messageIndex].content_json?.text || '';
    const newText = currentText + chunk;
    console.log('Updating message text from:', currentText, 'to:', newText);
    
    messages.value[messageIndex].content_json = { text: newText };
    
    // Update streaming state
    const streamingData = streamingMessages.value.get(message_id);
    if (streamingData) {
      streamingData.content = newText;
      streamingMessages.value.set(message_id, streamingData);
    }
  } else {
    // If start was missed, create the assistant message now
    const assistantMessage = {
      id: message_id,
      role: 'assistant',
      message_type: 'assistant',
      content_json: { text: chunk || '' },
      status: 'streaming',
      created_at: new Date().toISOString()
    };
    messages.value.push(assistantMessage);
    streamingMessages.value.set(message_id, { content: chunk || '', status: 'streaming', metadata });
    streamingStatus.value.set(message_id, 'streaming');
  }
};

const handleAssistantComplete = (data) => {
  console.log('🎯 Assistant Message Complete event:', data);
  const { message_id, status, metadata } = data;
  const messageIndex = messages.value.findIndex(m => m.id === message_id);
  if (messageIndex !== -1) {
    messages.value[messageIndex].status = 'complete';
  } else {
    // If no prior start/chunk, create a complete assistant message now
    const finalContent = (streamingMessages.value.get(message_id)?.content) || '';
    const assistantMessage = {
      id: message_id,
      role: 'assistant',
      message_type: 'assistant',
      content_json: { text: finalContent },
      status: 'complete',
      created_at: new Date().toISOString()
    };
    messages.value.push(assistantMessage);
  }
  
  // Update streaming state
  streamingStatus.value.set(message_id, 'complete');
  const streamingData = streamingMessages.value.get(message_id);
  if (streamingData) {
    streamingData.status = 'complete';
    streamingMessages.value.set(message_id, streamingData);
  }
};

const handleStreamingError = (data) => {
  console.log('🎯 Streaming Error event:', data);
  const { message_id, error_message } = data || {};
  if (!message_id) return;
  // Update message status to error
  const messageIndex = messages.value.findIndex(m => m.id === message_id);
  if (messageIndex !== -1) {
    messages.value[messageIndex].status = 'error';
  }
  // Update streaming state
  streamingStatus.value.set(message_id, 'error');
  const streamingData = streamingMessages.value.get(message_id) || {};
  streamingData.status = 'error';
  streamingMessages.value.set(message_id, streamingData);
};

// State Update Functions
const updateLLMStatus = (stage, message) => {
  llmStatus.value = { stage, message, timestamp: new Date().toISOString() };
};

const updateToolStatus = (toolName, status, result, error) => {
  toolStatus.value = { toolName, status, result, error, timestamp: new Date().toISOString() };
};

const addMessageToChat = (messageData) => {
  // Add real-time message to chat
  realTimeMessages.value.push(messageData);
};

const updateMessageStatus = (messageId, status) => {
  // Update message status in real-time
  const messageIndex = realTimeMessages.value.findIndex(m => m.message_id === messageId);
  if (messageIndex !== -1) {
    realTimeMessages.value[messageIndex].status = status;
  }
};

// Watch for session/history changes and rejoin WebSocket rooms
watch([() => props.selectedSession, () => props.historyId], ([newSession, newHistoryId], [oldSession, oldHistoryId]) => {
  console.log('Session/History watch triggered:', { newSession, newHistoryId, oldSession, oldHistoryId });
  
  // Leave old room if it exists
  if (oldSession && oldHistoryId) {
    const oldRoom = `chat/${oldSession.id}/${oldHistoryId}`;
    console.log('Leaving old room:', oldRoom);
    chatService.leaveRoom(oldRoom);
    cleanupWsListeners();
  }
  
  // Join new room if it exists
  if (newSession && newHistoryId) {
    const newRoom = `chat/${newSession.id}/${newHistoryId}`;
    console.log('Joining new room:', newRoom);
    chatService.joinRoom(newRoom);
    
    console.log('Setting up WebSocket event listeners...');
    // Re-attach event listeners
    wsUnsubs.value.push(chatService.onWebSocketEvent('llm_status', handleLLMStatus));
    wsUnsubs.value.push(chatService.onWebSocketEvent('tool_status', handleToolStatus));
    wsUnsubs.value.push(chatService.onWebSocketEvent('message_received', handleMessageReceived));
    wsUnsubs.value.push(chatService.onWebSocketEvent('message_processed', handleMessageProcessed));
    
    // Re-attach streaming event listeners
    wsUnsubs.value.push(chatService.onWebSocketEvent('assistant_message_started', handleAssistantStarted));
    wsUnsubs.value.push(chatService.onWebSocketEvent('assistant_message_chunk', handleAssistantChunk));
    wsUnsubs.value.push(chatService.onWebSocketEvent('assistant_message_complete', handleAssistantComplete));
    wsUnsubs.value.push(chatService.onWebSocketEvent('streaming_error', handleStreamingError));
    console.log('WebSocket event listeners attached successfully');
  } else {
    console.log('No session or history ID available for WebSocket setup');
  }
}, { immediate: true });

// Load messages for specific history
const loadMessages = async (historyId) => {
  if (!historyId || !chatService) {
    return;
  }
  
  try {
    loading.value = true;
    
    // Use the new ChatService method that requires both sessionId and historyId
    if (!props.selectedSession?.id) {
      messages.value = [];
      return;
    }
    
    const sessionId = props.selectedSession.id;
    const response = await chatService.getHistoryMessages(sessionId, historyId);
    
    // Backend returns {data: [...], total: X} - extract the actual messages array
    const messagesData = response?.data || response || [];
    
    // Force Vue to detect the change by creating a new array
    messages.value = [...messagesData];
    
    console.log('Messages loaded successfully:', messages.value.length);
    
  } catch (error) {
    console.error('Failed to load messages:', error);
    messages.value = [];
    // Emit error to parent component for toast notification
    emit('error', {
      message: 'Failed to load messages',
      details: error
    });
  } finally {
    loading.value = false;
  }
};

// Load messages when historyId changes
watch(() => props.historyId, async (newHistoryId) => {
  if (newHistoryId) {
    await loadMessages(newHistoryId);
  } else {
    messages.value = [];
  }
}, { immediate: true });

// React to selectedSession changes
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
    
    // Load messages for the new session if we have a history
    if (props.historyId) {
      loadMessages(props.historyId);
    }
  }
}, { immediate: true });

// Send message
const onSend = async () => {
  if (!inputText.value?.trim() || !props.historyId || !chatService) return;
  
  try {
    // Clear error states when sending new message
    streamingStatus.value.forEach((status, messageId) => {
      if (status === 'error') {
        streamingStatus.value.set(messageId, 'complete');
      }
    });
    
    // Clear streaming messages
    streamingMessages.value.clear();
    
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
      messages.value.push(userMessage);
    } catch (e) {
      console.error('Failed to append optimistic user message:', e);
    }
  } catch (error) {
    console.error('Failed to send message:', error);
  }
};

// Handle message deletion
const handleDeleteMessage = async (messageData) => {
  if (!messageData?.messageId || !props.historyId || !chatService || !props.selectedSession?.id) {
    console.error('Cannot delete message: Missing required data', messageData);
    return;
  }
  
  try {
    // Call the backend to delete the message
    const response = await chatService.deleteMessage(
      props.selectedSession.id, 
      props.historyId, 
      messageData.messageId
    );
    
    if (response) {
      // Remove the message from local state immediately
      messages.value = messages.value.filter(msg => msg.id !== messageData.messageId);
      
      // Emit success to parent for toast notification
      emit('deleteMessage', { success: true, messageData, response });
    }
  } catch (error) {
    console.error('Failed to delete message:', error);
    // Emit error to parent for toast notification
    emit('deleteMessage', { success: false, messageData, error });
  }
};

// Show tools
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
      
      availableTools.value = toolsArray;
    } else {
      availableTools.value = [];
    }
  } catch (error) {
    console.error('Failed to load tools:', error);
    availableTools.value = [];
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
  console.log('🔧 Extracted args:', args);

  try {
    console.log('🔧 Executing tool with form data:', formData);

    const response = await chatService.sendMessage(
      props.selectedSession.id,           // sessionId
      props.historyId,                    // ✅ historyId as separate parameter
      {
        message_type: 'tool_call',        // CORRECT: message_type field
        content: {                        // CORRECT: content wrapper
          tool: selectedTool.value.name,  // Use the tool name from the selectedTool object
          args: args                      // Use the extracted form data
        }
      }
    );

    console.log('Tool executed successfully:', response);

    // ✅ FIXED: Remove dummy message creation - let WebSocket events handle real messages
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

// Clear local messages (for when backend clears them)
const clearLocalMessages = () => {
  messages.value = [];
};

// Get the appropriate component for each message
const getMessageComponent = (message) => {
  const messageType = message.message_type || (message.role === 'assistant' ? 'assistant' : 'user');
  return chatMessageTypeManager.getMessageType(messageType);
};

// Check if message has a valid type
const hasValidMessageType = (message) => {
  const messageType = message.message_type || (message.role === 'assistant' ? 'assistant' : 'user');
  return chatMessageTypeManager.hasMessageType(messageType);
};

// Check if message is currently streaming
const isMessageStreaming = (messageId) => {
  return streamingStatus.value.get(messageId) === 'streaming';
};

// Get streaming content for a message
const getStreamingContent = (messageId) => {
  const streamingData = streamingMessages.value.get(messageId);
  return streamingData ? streamingData.content : '';
};

// Computed values
const hasHistory = computed(() => !!props.historyId);
const canSendMessage = computed(() => hasHistory.value && inputText.value?.trim());

// Button state management
const isStreaming = computed(() => {
  try {
    if (!streamingStatus.value || !(streamingStatus.value instanceof Map)) {
      return false;
    }
    return Array.from(streamingStatus.value.values()).some(status => status === 'streaming');
  } catch (error) {
    console.warn('Error computing isStreaming:', error);
    return false;
  }
});

const hasErrors = computed(() => {
  try {
    if (!streamingStatus.value || !(streamingStatus.value instanceof Map)) {
      return false;
    }
    return Array.from(streamingStatus.value.values()).some(status => status === 'error');
  } catch (error) {
    console.warn('Error computing hasErrors:', error);
    return false;
  }
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

const buttonLabel = computed(() => {
  if (isStreaming.value) return 'Stop';
  if (canRetry.value) return 'Retry';
  return 'Send';
});

const buttonSeverity = computed(() => {
  if (isStreaming.value) return 'danger';
  if (canRetry.value) return 'warning';
  return 'primary';
});

// Computed property for streaming status display
const showStreamingStatus = computed(() => {
  try {
    if (!streamingStatus.value || !(streamingStatus.value instanceof Map)) {
      return false;
    }
    return Array.from(streamingStatus.value.values()).some(status => status === 'streaming');
  } catch (error) {
    console.warn('Error computing showStreamingStatus:', error);
    return false;
  }
});

// Stop streaming functionality
const onStop = async () => {
  if (!props.selectedSession?.id || !chatService) return;
  
  try {
    const streamingMsg = messages.value.find(m => m.role === 'assistant' && m.status === 'streaming');
    let response;
    if (streamingMsg && props.historyId) {
      response = await chatService.cancelMessage(props.selectedSession.id, props.historyId, streamingMsg.id);
      console.log('Cancel message response', response);
    } else {
      return;
    }

    if (response && response.cancelled) {
      // Clear streaming status for all messages
      streamingStatus.value.forEach((status, messageId) => {
        if (status === 'streaming') {
          streamingStatus.value.set(messageId, 'complete');
        }
      });
      
      // Clear streaming messages
      streamingMessages.value.clear();
      
      // Update any streaming messages in the messages array to complete
      messages.value.forEach(msg => {
        if (msg.status === 'streaming') {
          msg.status = 'complete';
        }
      });
      
      console.log('Streaming cancelled successfully');
    }
  } catch (error) {
    console.error('Failed to cancel streaming:', error);
  }
};

// Retry functionality
const onRetry = async () => {
  if (!props.selectedSession?.id || !chatService) return;
  
  try {
    const response = await chatService.retryLastMessage(props.selectedSession.id);
    
    if (response?.status === 'processing') {
      // Clear error states for all messages
      streamingStatus.value.forEach((status, messageId) => {
        if (status === 'error') {
          streamingStatus.value.set(messageId, 'complete');
        }
      });
      
      // Clear streaming messages
      streamingMessages.value.clear();
      
      // Clear any error messages from the messages array
      messages.value.forEach(msg => {
        if (msg.status === 'error') {
          msg.status = 'complete';
        }
      });
      
      console.log('Retry initiated successfully');
    }
  } catch (error) {
    console.error('Failed to retry message:', error);
  }
};

// Expose methods for parent component
defineExpose({
  loadMessages,
  clearLocalMessages,
  refreshMessages: () => loadMessages(props.historyId),
  triggerRefresh: () => loadMessages(props.historyId),
  
  // Expose streaming methods
  isMessageStreaming,
  getStreamingContent,
  getStreamingStatus: () => Object.fromEntries(streamingStatus.value),
  getStreamingMessages: () => Object.fromEntries(streamingMessages.value)
});
</script>

<template>
  <div class="chat-container">
    <!-- Real-time Status Display -->
    <div v-if="llmStatus || toolStatus" class="real-time-status p-3 surface-100 border-round mb-2">
      <!-- LLM Status -->
      <div v-if="llmStatus" class="llm-status mb-2">
        <div class="flex align-items-center gap-2">
          <i class="pi pi-spin pi-spinner text-primary"></i>
          <span class="font-medium text-primary">{{ llmStatus.stage }}</span>
          <span class="text-color-secondary">{{ llmStatus.message }}</span>
        </div>
      </div>
      
      <!-- Tool Status -->
      <div v-if="toolStatus" class="tool-status">
        <div class="flex align-items-center gap-2">
          <i :class="[
            toolStatus.status === 'started' ? 'pi pi-spin pi-spinner' : 'pi pi-check-circle',
            toolStatus.status === 'completed' ? 'text-success' : toolStatus.status === 'failed' ? 'text-danger' : 'text-primary'
          ]"></i>
          <span class="font-medium">{{ toolStatus.toolName }}</span>
          <span class="text-color-secondary">{{ toolStatus.status }}</span>
          <span v-if="toolStatus.error" class="text-danger">({{ toolStatus.error }})</span>
        </div>
      </div>
      
      <!-- Streaming Status -->
      <div v-if="showStreamingStatus" class="streaming-status mt-2">
        <div class="flex align-items-center gap-2">
          <i class="pi pi-spin pi-spinner text-warning"></i>
          <span class="font-medium text-warning">AI is typing...</span>
          <span class="text-color-secondary">Streaming response in real-time</span>
        </div>
      </div>
    </div>
    
    <!-- Messages Area - Takes remaining space and scrolls -->
    <div class="messages-area">
      <div v-if="messages.length === 0 && !loading" class="text-center text-color-secondary p-4">
        <i class="pi pi-comments text-4xl mb-2"></i>
        <p>No messages yet. Start a conversation!</p>
      </div>
      
      <div v-else-if="loading" class="text-center text-color-secondary p-4">
        <i class="pi pi-spin pi-spinner text-2xl"></i>
        <p class="mt-2">Loading messages...</p>
      </div>
      
      <div v-else v-for="message in messages" :key="message.id">
        <component
          v-if="hasValidMessageType(message)"
          :is="message.role === 'user' ? OutgoingMessageContainer : IncomingMessageContainer"
          :message="message"
          :component="getMessageComponent(message)"
          :current-user-id="currentUserId"
          @delete-message="handleDeleteMessage"
        />
      </div>
    </div>

    <!-- Input Area - Fixed at bottom -->
    <div class="input-area">
      
      <!-- Tools Button -->
      <Button 
        icon="pi pi-box" 
        text 
        rounded 
        severity="secondary"
        @click="showTools"
        v-tooltip.bottom="'Available Tools'"
        :disabled="!hasHistory"
      />

      <!-- Input Field -->
      <span class="p-input-icon-right flex-grow-1 mx-2">
        <IconField>
          <InputText
            v-model="inputText"
            placeholder="Type a message..."
            class="w-full"
            @keyup.enter="buttonAction"
            :disabled="!hasHistory || isStreaming"
          />
          <InputIcon :class="buttonIcon" @click="buttonAction" />
        </IconField>
      </span>

      <!-- Single Button: Send/Stop/Retry -->
      <Button 
        :icon="buttonIcon"
        :label="buttonLabel"
        text 
        rounded 
        :severity="buttonSeverity"
        @click="buttonAction"
        :disabled="!hasHistory"
        class="mr-2"
      />

      <!-- Options Button -->
      <div class="relative">
        <Button 
          icon="pi pi-ellipsis-h" 
          text 
          rounded 
          severity="secondary"
          :disabled="!hasHistory"
          @click="toggleMoreMenu"
          aria-haspopup="true"
          aria-controls="more_menu"
        />
        <Badge 
          v-if="props.errors.length > 0" 
          :value="props.errors.length" 
          severity="danger" 
          class="absolute top-0 right-0 transform translate-x-1/2 -translate-y-1/2"
        />
      </div>
    </div>

    <!-- More Menu -->
    <Menu 
      ref="moreMenu" 
      id="more_menu" 
      :model="moreMenuItems" 
      :popup="true"
    />

    <!-- Error Dialog -->
    <ErrorDialog
      :visible="showErrorDialog"
      :errors="props.errors"
      @update:visible="showErrorDialog = $event"
    />

    <!-- Tools Dialog -->
    <AvailableToolsDialog
      :visible="showToolsDialog"
      :tools="availableTools"
      @update:visible="showToolsDialog = $event"
      @tool-selected="selectTool"
    />

    <!-- Tool Execution Dialog -->
    <ToolExecutionDialog
      ref="toolExecutionDialogRef"
      :selected-tool="selectedTool"
      @execute-tool="executeToolWithForm"
    />
  </div>
</template>

<style scoped>
/* Normal, working flexbox layout */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Messages area - normal flex behavior */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

/* Input area - normal fixed position */
.input-area {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-top: 1px solid var(--surface-border);
  background: var(--surface-section);
}

/* Button layout and spacing */
.input-area .p-button {
  flex-shrink: 0;
}

.input-area .p-button.mr-2 {
  margin-right: 0.5rem;
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

/* Real-time status display */
.real-time-status {
  border-left: 4px solid var(--primary-color);
  background: var(--surface-50);
}

.llm-status, .tool-status, .streaming-status {
  font-size: 0.875rem;
}

.llm-status .pi-spinner {
  animation: spin 1s linear infinite;
}

.tool-status .pi-spinner {
  animation: spin 1s linear infinite;
}

.streaming-status .pi-spinner {
  animation: spin 1s linear infinite;
}

.streaming-status {
  border-left: 3px solid var(--warning-color);
  background: var(--surface-100);
}

.streaming-indicator {
  border-left: 3px solid var(--warning-color);
  background: var(--surface-50);
  margin-left: 1rem;
  opacity: 0.8;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
