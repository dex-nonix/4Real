<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, inject, watch, nextTick } from 'vue';
import ErrorDialog from './ErrorDialog.vue';
import chatMessageTypeManager from './ChatMessageTypeManager.js';
import SystemMessage from './message-types/SystemMessage.vue';
import ToolMessage from './message-types/ToolMessage.vue';
import UserMessage from './message-types/UserMessage.vue';
import { IncomingMessageContainer, OutgoingMessageContainer } from './message-types/index.js';
import StreamingMessage from './message-types/StreamingMessage.vue';
import TurnHeader from './turns/TurnHeader.vue';
import TurnTimeline from './turns/TurnTimeline.vue';
import ChatInputArea from './ChatInputArea.vue';

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
const loading = ref(false);

// NEW: Turns state
const turnsById = reactive(new Map()); // turn_id -> { items: Map(seq->item), tools: Map(tool_run_id->{tool_name,status}) }
const orderedTurns = computed(() => {
  const arr = [];
  for (const [turnId, obj] of turnsById.entries()) {
    const seqs = Array.from(obj.items.keys()).sort((a, b) => a - b);
    const firstSeq = seqs[0] || 0;
    const lastSeq = seqs[seqs.length - 1] || firstSeq;
    arr.push({ turnId, firstSeq, lastSeq, obj });
  }
  return arr.sort((a, b) => a.firstSeq - b.firstSeq);
});

// Compute per-turn status for header
const computeTurnStatus = (turn) => {
  try {
    const items = Array.from(turn.obj.items.values());
    if (!items.length) return 'complete';
    const assistants = items.filter(i => i && i.role === 'assistant');
    if (assistants.some(i => i.status === 'error')) return 'error';
    if (assistants.length && assistants.every(i => i.status === 'complete')) return 'complete';
    return 'in_progress';
  } catch (_) {
    return 'in_progress';
  }
};

// WebSocket Real-time State
const llmStatus = ref(null);
const toolStatus = ref(null);
const realTimeMessages = ref([]);

// NEW: Streaming message state management
const streamingMessages = reactive(new Map()); // message_id -> { content, status, metadata }
const streamingStatus = reactive(new Map());   // message_id -> 'streaming' | 'complete' | 'error'



// Track active WebSocket unsubscribers to avoid duplicate handlers
const wsUnsubs = ref([]);
const wsEventHandlers = ref(new Map()); // Track registered handlers to prevent duplicates

// Helper function to register WebSocket event handlers without duplicates
const registerWsHandler = (event, handler) => {
  if (wsEventHandlers.value.has(event)) {
    const existingUnsub = wsEventHandlers.value.get(event);
    try { typeof existingUnsub === 'function' && existingUnsub(); } catch (_) { }
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
      wsUnsubs.value.forEach(unsub => { try { typeof unsub === 'function' && unsub(); } catch (_) { } });
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
  if (!turnsById.has(turnId)) {
    turnsById.set(turnId, { items: new Map(), tools: new Map() });
  }
  return turnsById.get(turnId);
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

  // Strict payload: require content_json for text roles
  if ((derivedType === 'assistant' || derivedType === 'user' || derivedType === 'system') && !incoming.content_json) {
    console.error('Invalid payload: content_json is required for text message types', incoming);
    return;
  }
  // Strict required fields
  if (!incoming.message_id || !incoming.role || !incoming.message_type || typeof incoming.seq === 'undefined' || !incoming.turn_id) {
    console.error('Invalid payload: required fields missing', incoming);
    return;
  }

  const idx = messages.value.findIndex(m => String(m.id) === String(incoming.message_id));
  const msgObj = {
    id: incoming.message_id,
    role: incoming.role,
    message_type: derivedType,
    content_json: incoming.content_json || null,
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

  console.log('WebSocket message_received:', incoming.message_id, incoming.role, incoming.message_type);

  if (idx !== -1) {
    // Update existing message - ensure reactivity by replacing the entire object
    messages.value.splice(idx, 1, { ...messages.value[idx], ...msgObj });
    console.log('Updated existing message at index:', idx);
  } else {
    // Add new message - ensure reactivity by using push
    messages.value.push({ ...msgObj });
    console.log('Added new message, total messages:', messages.value.length);
  }

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
      content_json: (incoming.content_json || null),
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
    // Update existing message reactively
    const updatedMessage = { ...messages.value[existingIndex], status: 'streaming' };
    messages.value.splice(existingIndex, 1, updatedMessage);
    console.log('Updated existing streaming message at index:', existingIndex);
  } else {
    const assistantMessage = {
      id: message_id,
      role: 'assistant',
      message_type: 'assistant',
      content_json: { text: '' },
      status: 'streaming',
      created_at: new Date().toISOString(),
      seq: metadata?.seq,
      turn_id: metadata?.turn_id,
      tool_run_id: metadata?.tool_run_id
    };
    messages.value.push(assistantMessage);
    console.log('Added new streaming message to UI. Total messages:', messages.value.length);
  }

  // Track streaming state
  streamingMessages.set(message_id, { content: '', status: 'streaming', metadata });
  streamingStatus.set(message_id, 'streaming');
  if (metadata && metadata.turn_id && metadata.seq) {
    upsertTurnItem({
      id: message_id,
      role: 'assistant',
      message_type: 'assistant',
      seq: metadata.seq,
      turn_id: metadata.turn_id,
      content_json: { text: '' },
      status: 'streaming',
      created_at: new Date().toISOString(),
      tool_run_id: metadata.tool_run_id
    });
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
    console.log('Updating message text from:', currentText.length, 'chars to:', newText.length, 'chars');

    // Update message reactively
    const updatedMessage = {
      ...messages.value[messageIndex],
      content_json: { text: newText }
    };
    messages.value.splice(messageIndex, 1, updatedMessage);

    // Update streaming state
    const streamingData = streamingMessages.get(message_id);
    if (streamingData) {
      streamingData.content = newText;
      streamingMessages.set(message_id, streamingData);
    }
  } else {
    // If start was missed, create the assistant message now
    console.log('Chunk received but no existing message found, creating new one');
    const assistantMessage = {
      id: message_id,
      role: 'assistant',
      message_type: 'assistant',
      content_json: { text: chunk || '' },
      status: 'streaming',
      created_at: new Date().toISOString(),
      seq: metadata?.seq,
      turn_id: metadata?.turn_id,
      tool_run_id: metadata?.tool_run_id
    };
    messages.value.push(assistantMessage);
    streamingMessages.set(message_id, { content: chunk || '', status: 'streaming', metadata });
    streamingStatus.set(message_id, 'streaming');
  }
  if (metadata && metadata.turn_id && metadata.seq) {
    const sd = streamingMessages.get(message_id);
    const text = sd && sd.content ? sd.content : (chunk || '');
    upsertTurnItem({ id: message_id, role: 'assistant', message_type: 'assistant', seq: metadata.seq, turn_id: metadata.turn_id, content_json: { text }, status: 'streaming', created_at: new Date().toISOString() });
  }
};

const handleAssistantComplete = (data) => {
  console.log('🎯 Assistant Message Complete event:', data);
  const { message_id, metadata } = data;
  const messageIndex = messages.value.findIndex(m => m.id === message_id);
  if (messageIndex !== -1) {
    // Update message reactively
    const updatedMessage = { ...messages.value[messageIndex], status: 'complete' };
    messages.value.splice(messageIndex, 1, updatedMessage);
    console.log('Marked message as complete at index:', messageIndex);
  } else {
    // If no prior start/chunk, create a complete assistant message now
    console.log('Complete event received but no existing message found, creating final message');
    const finalContent = (streamingMessages.get(message_id)?.content) || '';
    const assistantMessage = {
      id: message_id,
      role: 'assistant',
      message_type: 'assistant',
      content_json: { text: finalContent },
      status: 'complete',
      created_at: new Date().toISOString(),
      seq: metadata?.seq,
      turn_id: metadata?.turn_id,
      tool_run_id: metadata?.tool_run_id
    };
    messages.value.push(assistantMessage);
  }

  // Update streaming state
  streamingStatus.set(message_id, 'complete');
  const streamingData = streamingMessages.get(message_id);
  if (streamingData) {
    streamingData.status = 'complete';
    streamingMessages.set(message_id, streamingData);
  }
  if (metadata && metadata.turn_id && metadata.seq) {
    const sd = streamingMessages.get(message_id);
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
  streamingStatus.set(message_id, 'error');
  const streamingData = streamingMessages.get(message_id) || {};
  streamingData.status = 'error';
  streamingMessages.set(message_id, streamingData);
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

    console.log('Messages loaded successfully:', messages.value.length, 'messages');
    console.log('Message breakdown:', {
      total: messages.value.length,
      user: messages.value.filter(m => m.role === 'user').length,
      assistant: messages.value.filter(m => m.role === 'assistant').length,
      system: messages.value.filter(m => m.role === 'system').length,
      tool: messages.value.filter(m => m.role === 'tool_result' || m.message_type === 'tool_result').length
    });

    // Rebuild turnsById from loaded messages with better error handling
    turnsById.clear();
    streamingMessages.clear();
    streamingStatus.clear();

    for (const m of messages.value) {
      console.log('Processing message:', m.id, m.role, m.message_type, 'turn_id:', m.turn_id, 'seq:', m.seq);

      if (m.turn_id && m.seq) {
        upsertTurnItem({
          id: m.id,
          role: m.role,
          message_type: m.message_type || (m.role === 'assistant' ? 'assistant' : m.role),
          seq: m.seq,
          turn_id: m.turn_id,
          status: m.status,
          content_json: m.content_json,
          tool_run_id: m.tool_run_id,
          tool_name: m.tool_name,
          tool_args: m.tool_args,
          execution_status: m.execution_status,
          result: m.result,
          executed_by: m.executed_by,
          execution_time: m.execution_time,
          execution_path: m.execution_path,
          created_at: m.created_at
        });
      }

      // Ensure streaming state is properly initialized for any streaming messages
      if (m.status === 'streaming') {
        streamingMessages.set(m.id, {
          content: m.content_json?.text || '',
          status: 'streaming',
          metadata: { turn_id: m.turn_id, seq: m.seq }
        });
        streamingStatus.set(m.id, 'streaming');
      }
    }

    console.log('Turns rebuilt. Total turns:', turnsById.size);
    console.log('Ordered turns:', orderedTurns.value.length);

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

// Combined watcher for both historyId and selectedSession to prevent race conditions
watch([() => props.historyId, () => props.selectedSession], async ([newHistoryId, newSession], [oldHistoryId, oldSession]) => {
  // Only load messages if we have both a valid session and history
  if (newSession && newHistoryId) {
    // Avoid duplicate loading if session changed but history stayed the same
    if (oldSession?.id !== newSession.id || oldHistoryId !== newHistoryId) {
      console.log('Loading messages for session:', newSession.id, 'history:', newHistoryId);
      await loadMessages(newHistoryId);
    }
  } else {
    // Clear messages if either session or history becomes invalid
    messages.value = [];
    turnsById.clear();
  }
}, { immediate: true });


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
      // Also remove from turn timeline immediately
      try {
        for (const [turnId, obj] of turnsById.entries()) {
          const toDelete = [];
          for (const [seq, item] of obj.items.entries()) {
            if (item && String(item.id) === String(messageData.messageId)) {
              toDelete.push(seq);
            }
          }
          toDelete.forEach(seq => obj.items.delete(seq));
          if (obj.items.size === 0 && obj.tools.size === 0) {
            turnsById.delete(turnId);
          }
        }
      } catch (_) { }

      // Emit success to parent for toast notification
      emit('deleteMessage', { success: true, messageData, response });
    }
  } catch (error) {
    console.error('Failed to delete message:', error);
    // Emit error to parent for toast notification
    emit('deleteMessage', { success: false, messageData, error });
  }
};




// Clear local messages (for when backend clears them)
const clearLocalMessages = () => {
  console.log('Clearing all local messages and state');
  messages.value = [];
  try {
    if (turnsById && typeof turnsById.clear === 'function') {
      turnsById.clear();
    }
    if (streamingMessages && typeof streamingMessages.clear === 'function') {
      streamingMessages.clear();
    }
    if (streamingStatus && typeof streamingStatus.clear === 'function') {
      streamingStatus.clear();
    }
    // Also clear real-time messages
    realTimeMessages.value = [];
  } catch (error) {
    console.error('Error clearing local messages:', error);
  }
};

// Force re-render messages (useful for debugging rendering issues)
const forceReRender = () => {
  console.log('Force re-rendering messages...');
  // Trigger reactivity by temporarily clearing and re-setting
  const currentMessages = [...messages.value];
  messages.value = [];
  // Use nextTick to ensure the clear is processed before re-setting
  nextTick(() => {
    messages.value = currentMessages;
    console.log('Re-rendered messages. Total:', messages.value.length);
  });
};

// Get the appropriate component for each message
const getMessageComponent = (message) => {
  const messageType = message.message_type || (message.role === 'assistant' ? 'assistant' : 'user');
  return chatMessageTypeManager.getMessageType(messageType);
};

//

// Check if message is currently streaming
const isMessageStreaming = (messageId) => {
  return streamingStatus.get(messageId) === 'streaming';
};

// Get streaming content for a message
const getStreamingContent = (messageId) => {
  const streamingData = streamingMessages.get(messageId);
  return streamingData ? streamingData.content : '';
};


// Computed property for streaming status display
const showStreamingStatus = computed(() => { try { if (!(streamingStatus instanceof Map)) return false; return Array.from(streamingStatus.values()).some(status => status === 'streaming'); } catch { return false; } });


// Expose methods for parent component
defineExpose({
  loadMessages,
  clearLocalMessages,
  refreshMessages: () => loadMessages(props.historyId),
  triggerRefresh: () => loadMessages(props.historyId),
  forceReRender,

  // Expose streaming methods
  isMessageStreaming,
  getStreamingContent,
  getStreamingStatus: () => Object.fromEntries(streamingStatus),
  getStreamingMessages: () => Object.fromEntries(streamingMessages),

  // Debug helpers
  getMessageCount: () => messages.value.length,
  getTurnCount: () => turnsById.size,
  getStreamingCount: () => streamingStatus.size
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
          <TurnHeader :turn-id="turn.turnId" :first-seq="turn.firstSeq" :last-seq="turn.lastSeq"
            :tools-count="turn.obj.tools.size" :status="computeTurnStatus(turn)" />
          <TurnTimeline :items="Array.from(turn.obj.items.values())"
            :tools-by-run-id="Object.fromEntries(turn.obj.tools)">
            <template #item="{ item }">
              <component :is="item.role === 'user' ? OutgoingMessageContainer : IncomingMessageContainer"
                :message="item" :component="getMessageComponent(item)" :current-user-id="currentUserId"
                @delete-message="handleDeleteMessage" />
            </template>
          </TurnTimeline>
        </div>
      </div>
    </div>

    <!-- Input Area Component -->
    <ChatInputArea
      :session-id="sessionId"
      :history-id="historyId"
      :selected-session="selectedSession"
      :errors="errors"
      :available-tools="availableTools"
      :streaming-status="streamingStatus"
      :streaming-messages="streamingMessages"
      :messages="messages"
      @send-message="$emit('sendMessage', $event)"
      @error="$emit('error', $event)"
    />

    <!-- Error Dialog -->
    <ErrorDialog :visible="showErrorDialog" :errors="props.errors" @update:visible="showErrorDialog = $event" />


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


/* Real-time status display */
.real-time-status {
  border-left: 4px solid var(--primary-color);
  background: var(--surface-50);
}

.llm-status,
.tool-status,
.streaming-status {
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
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}
</style>
