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
import SystemMessage from './message-types/SystemMessage.vue';
import ToolMessage from './message-types/ToolMessage.vue';
import UserMessage from './message-types/UserMessage.vue';
import { IncomingMessageContainer, OutgoingMessageContainer } from './message-types/index.js';
import StreamingMessage from './message-types/StreamingMessage.vue';
import AvailableToolsDialog from './AvailableToolsDialog.vue';
import ToolExecutionDialog from './ToolExecutionDialog.vue';
import TurnHeader from './turns/TurnHeader.vue';
import TurnTimeline from './turns/TurnTimeline.vue';

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

// NEW: Turns state
const turnsById = ref(new Map()); // turn_id -> { items: Map(seq->item), tools: Map(tool_run_id->{tool_name,status}) }
const orderedTurns = computed(() => {
  const arr = [];
  for (const [turnId, obj] of turnsById.value.entries()) {
    const seqs = Array.from(obj.items.keys()).sort((a, b) => a - b);
    const firstSeq = seqs[0] || 0;
    const lastSeq = seqs[seqs.length - 1] || firstSeq;
    arr.push({ turnId, firstSeq, lastSeq, obj });
  }
  return arr.sort((a, b) => a.firstSeq - b.firstSeq);
});

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
const wsEventHandlers = ref(new Map()); // Track registered handlers to prevent duplicates

// Helper function to register WebSocket event handlers without duplicates
const registerWsHandler = (event, handler) => {
  if (wsEventHandlers.value.has(event)) {
    const existingUnsub = wsEventHandlers.value.get(event);
    try { typeof existingUnsub === 'function' && existingUnsub(); } catch (_) {}
  }
  const unsub = chatService.onWebSocketEvent(event, handler);
  wsEventHandlers.value.set(event, unsub);
  wsUnsubs.value.push(unsub);
  return unsub;
};

const cleanupWsListeners = () => {
  try {
    if (wsEventHandlers.value.size > 0) {
      wsEventHandlers.value.forEach((unsub) => {
        try { typeof unsub === 'function' && unsub(); } catch (e) { }
      });
      wsEventHandlers.value.clear();
    }
    if (Array.isArray(wsUnsubs.value)) {
      wsUnsubs.value.forEach(unsub => { try { typeof unsub === 'function' && unsub(); } catch (_) {} });
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
  chatMessageTypeManager.registerMessageType('tool_call', ToolMessage);
});

// Cleanup WebSocket resources on unmount
onUnmounted(() => {
  if (props.selectedSession && props.historyId) {
    const room = `chat/${props.selectedSession.id}/${props.historyId}`;
    chatService.leaveRoom(room);
  }
  cleanupWsListeners();
});

// Helpers to upsert into turns
const ensureTurn = (turnId) => {
  if (!turnId) return null;
  if (!turnsById.value.has(turnId)) {
    turnsById.value.set(turnId, { items: new Map(), tools: new Map() });
  }
  return turnsById.value.get(turnId);
};

const upsertTurnItem = (payload) => {
  const { turn_id, seq } = payload;
  if (!turn_id || !seq) return;
  const turn = ensureTurn(turn_id);
  if (!turn) return;
  const item = Object.assign({}, payload);
  turn.items.set(Number(seq), item);
};

const upsertToolRun = (payload) => {
  const { turn_id, tool_run_id, tool_name, status } = payload;
  if (!turn_id || !tool_run_id) return;
  const turn = ensureTurn(turn_id);
  if (!turn) return;
  const existing = turn.tools.get(tool_run_id) || {};
  turn.tools.set(tool_run_id, Object.assign({}, existing, { tool_name, status }));
};

// WebSocket Event Handlers
const handleLLMStatus = (data) => {
  llmStatus.value = { stage: data.stage, message: data.message, timestamp: data.timestamp };
};

const handleToolStatus = (data) => {
  toolStatus.value = { toolName: data.tool_name, status: data.status, result: data.result, error: data.error, timestamp: data.timestamp };
  if (data.turn_id && data.tool_run_id) {
    upsertToolRun({ turn_id: data.turn_id, tool_run_id: data.tool_run_id, tool_name: data.tool_name, status: data.status });
  }
};

const handleMessageReceived = (data) => {
  const incoming = Object.assign({}, data);
  const derivedType = incoming.message_type
    || (incoming.role === 'assistant' ? 'assistant'
        : incoming.role === 'user' ? 'user'
        : incoming.role === 'system' ? 'system'
        : 'tool_result');
  incoming.message_type = derivedType;

  try {
    const idx = messages.value.findIndex(m => String(m.id) === String(incoming.message_id));
    const msgObj = {
      id: incoming.message_id,
      role: incoming.role,
      message_type: derivedType,
      content_json: (incoming.content_json || incoming.content || null),
      status: incoming.status || 'complete',
      created_at: incoming.timestamp || new Date().toISOString(),
      tool_name: incoming.tool_name,
      tool_args: incoming.tool_args,
      execution_status: incoming.execution_status,
      result: incoming.result,
      executed_by: incoming.executed_by,
      execution_time: incoming.execution_time,
      execution_path: incoming.execution_path,
      seq: incoming.seq,
      turn_id: incoming.turn_id,
      tool_run_id: incoming.tool_run_id,
      run_id: incoming.run_id
    };
    if (idx !== -1) messages.value[idx] = Object.assign({}, messages.value[idx], msgObj);
    else messages.value.push(msgObj);
  } catch (_) {}

  if (incoming.turn_id && incoming.seq) {
    upsertTurnItem({
      id: incoming.message_id,
      role: incoming.role,
      message_type: incoming.message_type,
      seq: incoming.seq,
      turn_id: incoming.turn_id,
      tool_run_id: incoming.tool_run_id,
      tool_name: incoming.tool_name,
      tool_args: incoming.tool_args,
      execution_status: incoming.execution_status,
      result: incoming.result,
      executed_by: incoming.executed_by,
      execution_time: incoming.execution_time,
      execution_path: incoming.execution_path,
      content_json: (incoming.content_json || incoming.content || null),
      created_at: incoming.timestamp
    });
  }

  if (incoming.tool_run_id && incoming.turn_id) {
    upsertToolRun({ turn_id: incoming.turn_id, tool_run_id: incoming.tool_run_id, tool_name: incoming.tool_name, status: incoming.execution_status || incoming.status });
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
  if (metadata && metadata.turn_id && metadata.seq) {
    upsertTurnItem({ id: message_id, role: 'assistant', message_type: 'assistant', seq: metadata.seq, turn_id: metadata.turn_id, created_at: new Date().toISOString(), status: 'streaming' });
  }
};

const handleAssistantChunk = (data) => {
  console.log('🎯 Assistant Message Chunk event:', data);
  // Find existing assistant message and append chunk
  const { message_id, chunk, metadata } = data;
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
  if (metadata && metadata.turn_id && metadata.seq) {
    const sd = streamingMessages.value.get(message_id);
    const text = sd && sd.content ? sd.content : (chunk || '');
    upsertTurnItem({ id: message_id, role: 'assistant', message_type: 'assistant', seq: metadata.seq, turn_id: metadata.turn_id, content_json: { text }, status: 'streaming', created_at: new Date().toISOString() });
  }
};

const handleAssistantComplete = (data) => {
  console.log('🎯 Assistant Message Complete event:', data);
  const { message_id, metadata } = data;
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
  if (metadata && metadata.turn_id && metadata.seq) {
    const sd = streamingMessages.value.get(message_id);
    const finalText = (sd && sd.content) ? sd.content : '';
    upsertTurnItem({ id: message_id, role: 'assistant', message_type: 'assistant', seq: metadata.seq, turn_id: metadata.turn_id, content_json: { text: finalText }, status: 'complete', created_at: new Date().toISOString() });
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

// State Update Functions (inline in handlers, helpers not needed) — removed
const updateMessageStatus = (messageId, status) => { const messageIndex = realTimeMessages.value.findIndex(m => m.message_id === messageId); if (messageIndex !== -1) { realTimeMessages.value[messageIndex].status = status; } };

// Watch for session/history changes and rejoin WebSocket rooms
watch([() => props.selectedSession, () => props.historyId], ([newSession, newHistoryId], [oldSession, oldHistoryId]) => {
  if (oldSession && oldHistoryId) {
    const oldRoom = `chat/${oldSession.id}/${oldHistoryId}`;
    chatService.leaveRoom(oldRoom);
    cleanupWsListeners();
  }
  if (newSession && newHistoryId) {
    const newRoom = `chat/${newSession.id}/${newHistoryId}`;
    chatService.joinRoom(newRoom);
    registerWsHandler('llm_status', handleLLMStatus);
    registerWsHandler('tool_status', handleToolStatus);
    registerWsHandler('message_received', handleMessageReceived);
    registerWsHandler('message_processed', handleMessageProcessed);
    registerWsHandler('assistant_message_started', handleAssistantStarted);
    registerWsHandler('assistant_message_chunk', handleAssistantChunk);
    registerWsHandler('assistant_message_complete', handleAssistantComplete);
    registerWsHandler('streaming_error', handleStreamingError);
  }
}, { immediate: true });

// Load messages for specific history
const loadMessages = async (historyId) => {
  if (!historyId || !chatService) return;
  
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
    
    // Rebuild turnsById from loaded messages
    turnsById.value.clear();
    for (const m of messages.value) {
      if (m.turn_id && m.seq) {
        upsertTurnItem({ id: m.id, role: m.role, message_type: m.message_type || (m.role === 'assistant' ? 'assistant' : m.role), seq: m.seq, turn_id: m.turn_id, tool_run_id: m.tool_run_id, tool_name: m.tool_name, tool_args: m.tool_args, execution_status: m.execution_status, result: m.result, executed_by: m.executed_by, execution_time: m.execution_time, execution_path: m.execution_path, created_at: m.created_at });
      }
    }

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
watch(() => props.historyId, async (newHistoryId) => { if (newHistoryId) await loadMessages(newHistoryId); else messages.value = []; }, { immediate: true });

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

// Clear local messages (for when backend clears them)
const clearLocalMessages = () => {
  messages.value = [];
  try {
    if (turnsById.value && typeof turnsById.value.clear === 'function') {
      turnsById.value.clear();
    }
    if (streamingMessages.value && typeof streamingMessages.value.clear === 'function') {
      streamingMessages.value.clear();
    }
    if (streamingStatus.value && typeof streamingStatus.value.clear === 'function') {
      streamingStatus.value.clear();
    }
  } catch (_) {}
};

// Get the appropriate component for each message
const getMessageComponent = (message) => {
  const messageType = message.message_type || (message.role === 'assistant' ? 'assistant' : 'user');
  return chatMessageTypeManager.getMessageType(messageType);
};

//

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

// Button state management
const isStreaming = computed(() => { try { if (!(streamingStatus.value instanceof Map)) return false; return Array.from(streamingStatus.value.values()).some(status => status === 'streaming'); } catch { return false; } });
const hasErrors = computed(() => { try { if (!(streamingStatus.value instanceof Map)) return false; return Array.from(streamingStatus.value.values()).some(status => status === 'error'); } catch { return false; } });
const canRetry = computed(() => hasErrors.value && !isStreaming.value);

const buttonIcon = computed(() => { if (isStreaming.value) return 'pi pi-stop'; if (canRetry.value) return 'pi pi-refresh'; return 'pi pi-send'; });
const buttonAction = computed(() => { if (isStreaming.value) return onStop; if (canRetry.value) return onRetry; return onSend; });
const buttonLabel = computed(() => { if (isStreaming.value) return 'Stop'; if (canRetry.value) return 'Retry'; return 'Send'; });
const buttonSeverity = computed(() => { if (isStreaming.value) return 'danger'; if (canRetry.value) return 'warning'; return 'primary'; });

// Computed property for streaming status display
const showStreamingStatus = computed(() => { try { if (!(streamingStatus.value instanceof Map)) return false; return Array.from(streamingStatus.value.values()).some(status => status === 'streaming'); } catch { return false; } });

// Stop streaming functionality
const onStop = async () => { if (!props.selectedSession?.id || !chatService) return; try { const streamingMsg = messages.value.find(m => m.role === 'assistant' && m.status === 'streaming'); let response; if (streamingMsg && props.historyId) response = await chatService.cancelMessage(props.selectedSession.id, props.historyId, streamingMsg.id); else return; if (response && response.cancelled) { streamingStatus.value.forEach((status, messageId) => { if (status === 'streaming') streamingStatus.value.set(messageId, 'complete'); }); streamingMessages.value.clear(); messages.value.forEach(msg => { if (msg.status === 'streaming') { msg.status = 'complete'; } }); } } catch { } };

// Retry functionality
const onRetry = async () => { if (!props.selectedSession?.id || !chatService) return; try { const response = await chatService.retryLastMessage(props.selectedSession.id); if (response?.status === 'processing') { streamingStatus.value.forEach((status, messageId) => { if (status === 'error') streamingStatus.value.set(messageId, 'complete'); }); streamingMessages.value.clear(); messages.value.forEach(msg => { if (msg.status === 'error') { msg.status = 'complete'; } }); } } catch { } };

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
      <div v-if="orderedTurns.length === 0 && !loading" class="text-center text-color-secondary p-4">
        <i class="pi pi-comments text-4xl mb-2"></i>
        <p>No messages yet. Start a conversation!</p>
      </div>
      
      <div v-else-if="loading" class="text-center text-color-secondary p-4">
        <i class="pi pi-spin pi-spinner text-2xl"></i>
        <p class="mt-2">Loading messages...</p>
      </div>
      
      <div v-else>
        <div v-for="turn in orderedTurns" :key="turn.turnId" class="mb-3">
          <TurnHeader :turn-id="turn.turnId" :first-seq="turn.firstSeq" :last-seq="turn.lastSeq" :tools-count="turn.obj.tools.size" :status="'in_progress'" />
          <TurnTimeline :items="Array.from(turn.obj.items.values())" :tools-by-run-id="Object.fromEntries(turn.obj.tools)" >
            <template #item="{ item }">
              <component
                :is="item.role === 'user' ? OutgoingMessageContainer : IncomingMessageContainer"
                :message="item"
                :component="getMessageComponent(item)"
                :current-user-id="currentUserId"
                @delete-message="handleDeleteMessage"
              />
            </template>
          </TurnTimeline>
        </div>
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
