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
import MessageContainer from './message-types/MessageContainer.vue';
import TextMessage from './message-types/TextMessage.vue';
import SystemMessage from './message-types/SystemMessage.vue';
import ToolMessage from './message-types/ToolMessage.vue';
import UserMessage from './message-types/UserMessage.vue';
import Dialog from 'primevue/dialog';
import ToolExecutionDialog from './ToolExecutionDialog.vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

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

// Session-specific input text storage
const sessionInputTexts = ref(new Map());

// Tools state
const showToolsDialog = ref(false);
const availableTools = ref([]);
const toolsLoading = ref(false);
const selectedTool = ref(null);
const toolExecutionDialogRef = ref(null);

// Register all message types with the manager
onMounted(() => {
  chatMessageTypeManager.registerMessageType('text', TextMessage);
  chatMessageTypeManager.registerMessageType('system', SystemMessage);
  chatMessageTypeManager.registerMessageType('tool', ToolMessage);
  chatMessageTypeManager.registerMessageType('user', UserMessage);
  
  // WebSocket Integration: Join chat room and listen for real-time events
  if (props.selectedSession && props.historyId) {
    const room = `chat/${props.selectedSession.id}/${props.historyId}`;
    
    // Use SIMPLE WebSocket methods
    chatService.joinRoom(room);
    
    // Listen for real-time events using SIMPLE methods
    chatService.onWebSocketEvent('llm_status', handleLLMStatus);
    chatService.onWebSocketEvent('tool_status', handleToolStatus);
    chatService.onWebSocketEvent('message_received', handleMessageReceived);
    chatService.onWebSocketEvent('message_processed', handleMessageProcessed);
  }
});

// Cleanup WebSocket resources on unmount
onUnmounted(() => {
  if (props.selectedSession && props.historyId) {
    const room = `chat/${props.selectedSession.id}/${props.historyId}`;
    chatService.leaveRoom(room);
  }
});

// WebSocket Event Handlers - NO NEW CLASSES
const handleLLMStatus = (data) => {
  const { stage, message, timestamp } = data;
  console.log('LLM Status:', stage, message, timestamp);
  // Update UI state based on LLM stage
  updateLLMStatus(stage, message);
};

const handleToolStatus = (data) => {
  const { tool_name, status, result, error, timestamp } = data;
  console.log('Tool Status:', tool_name, status, result, error);
  // Update UI state based on tool status
  updateToolStatus(tool_name, status, result, error);
};

const handleMessageReceived = (data) => {
  const { message_id, role, content, timestamp } = data;
  console.log('Message Received:', message_id, role, content);
  // Add message to chat
  addMessageToChat(data);
};

const handleMessageProcessed = (data) => {
  const { message_id, status, timestamp } = data;
  console.log('Message Processed:', message_id, status);
  // Update message status
  updateMessageStatus(message_id, status);
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
  // Leave old room if it exists
  if (oldSession && oldHistoryId) {
    const oldRoom = `chat/${oldSession.id}/${oldHistoryId}`;
    chatService.leaveRoom(oldRoom);
  }
  
  // Join new room if it exists
  if (newSession && newHistoryId) {
    const newRoom = `chat/${newSession.id}/${newHistoryId}`;
    chatService.joinRoom(newRoom);
    
    // Re-attach event listeners
    chatService.onWebSocketEvent('llm_status', handleLLMStatus);
    chatService.onWebSocketEvent('tool_status', handleToolStatus);
    chatService.onWebSocketEvent('message_received', handleMessageReceived);
    chatService.onWebSocketEvent('message_processed', handleMessageProcessed);
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
    const messageData = {
      historyId: props.historyId,
      text: inputText.value.trim(),
    };
    
    // Save current input text for this session before clearing
    if (props.selectedSession?.id) {
      sessionInputTexts.value.set(props.selectedSession.id, inputText.value);
    }
    
    // Emit event for parent component
    emit('sendMessage', messageData);
    
    // Clear input after sending
    inputText.value = '';
    
    // Reload messages to get the new message
    await loadMessages(props.historyId);
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

// Execute tool
const executeTool = async (toolName) => {
  if (!props.selectedSession?.persona_id || !props.historyId || !chatService) {
    console.error('Cannot execute tool: Missing required data');
    return;
  }
  
  try {
    // Execute tool using the existing ChatService
    const response = await chatService.executeTool(
      props.selectedSession.persona_id,
      toolName,
      {}, // Default empty args
      props.historyId,
      null, // message_id is optional
      props.selectedSession.id // session_id for WebSocket events
    );
    
    console.log('Tool executed successfully:', response);
    
    // Close tools dialog
    showToolsDialog.value = false;
    
    // Refresh messages to show tool result
    await loadMessages(props.historyId);
    
  } catch (error) {
    console.error('Tool execution failed:', error);
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
  
  try {
    console.log('🔧 Executing tool with form data:', formData);
    
    // Extract the actual form data from DynamicForm's submit event
    const args = formData.__full || formData.args || {};
    console.log('🔧 Extracted args:', args);
    
    // Execute tool using the existing ChatService
    const response = await chatService.executeTool(
      props.selectedSession.persona_id,
      selectedTool.value.name, // Use the tool name from the selectedTool object
      args, // Use the extracted form data
      props.historyId,
      null, // message_id is optional
      props.selectedSession.id // session_id for WebSocket events
    );
    
    console.log('Tool executed successfully:', response);
    
    // Create a tool message locally to show in chat immediately
    const toolMessage = {
      id: Date.now(), // Temporary ID
      message_type: 'tool',
      role: 'tool',
      content_json: {
        toolName: selectedTool.value.name,
        toolParams: args,
        executionStatus: response.data?.status === 'success' ? 'success' : 'error',
        result: response.data,
        executedBy: 'user',
        executionTime: new Date().toISOString()
      },
      created_at: new Date().toISOString()
    };
    
    // Add the tool message to the local messages array
    messages.value.push(toolMessage);
    
    // Close tool form
    showToolsDialog.value = false;
    selectedTool.value = null;
    
    // Refresh messages to get the official backend message (optional)
    await loadMessages(props.historyId);
    
  } catch (error) {
    console.error('Tool execution failed:', error);
    
    // Create an error tool message
    const errorToolMessage = {
      id: Date.now(),
      message_type: 'tool',
      role: 'tool',
      content_json: {
        toolName: selectedTool.value?.name || 'Unknown Tool',
        toolParams: args || {},
        executionStatus: 'error',
        result: { error: error.message || 'Tool execution failed' },
        executedBy: 'user',
        executionTime: new Date().toISOString()
      },
      created_at: new Date().toISOString()
    };
    
    messages.value.push(errorToolMessage);
  }
};

// Clear local messages (for when backend clears them)
const clearLocalMessages = () => {
  messages.value = [];
};

// Get the appropriate component for each message
const getMessageComponent = (message) => {
  const messageType = message.message_type || 'text';
  const component = chatMessageTypeManager.getMessageType(messageType);
  return component;
};

// Check if message has a valid type
const hasValidMessageType = (message) => {
  const messageType = message.message_type || 'text';
  const hasType = chatMessageTypeManager.hasMessageType(messageType);
  return hasType;
};

// Computed values
const hasHistory = computed(() => !!props.historyId);
const canSendMessage = computed(() => hasHistory.value && inputText.value?.trim());

// Expose methods for parent component
defineExpose({
  loadMessages,
  clearLocalMessages,
  refreshMessages: () => loadMessages(props.historyId),
  triggerRefresh: () => loadMessages(props.historyId)
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
        <!-- Use MessageContainer wrapper for consistent styling -->
        <MessageContainer
          v-if="hasValidMessageType(message)"
          :message="message"
          :currentUserId="currentUserId"
        >
          <template #content>
            <component
              :is="getMessageComponent(message)"
              :message="message"
              :currentUserId="currentUserId"
              @delete-message="handleDeleteMessage"
            />
          </template>
        </MessageContainer>
      </div>
    </div>

    <!-- Input Area - Fixed at bottom -->
    <div class="input-area">
      <!-- Debug info -->
      <div class="text-xs text-500 mr-2">
        Debug: historyId = {{ props.historyId }}, persona_id = {{ props.selectedSession?.persona_id }}
      </div>
      
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
            @keyup.enter="onSend"
            :disabled="!hasHistory"
          />
          <InputIcon class="pi pi-send" @click="onSend" />
        </IconField>
      </span>

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
    <Dialog 
      v-model:visible="showToolsDialog" 
      header="Available Tools" 
      modal 
      :style="{ width: '90vw', maxWidth: '700px' }"
      class="p-dialog-sm"
    >
      <div v-if="availableTools.length > 0">
        <DataTable 
          :value="availableTools" 
          class="p-datatable-sm"
          :showGridlines="true"
          stripedRows
          responsiveLayout="scroll"
        >
          <Column field="name" header="Tool" style="width: 40%">
            <template #body="{ data }">
              <div class="font-mono text-sm">{{ data.name }}</div>
            </template>
          </Column>
          
          <Column field="description" header="Description" style="width: 45%">
            <template #body="{ data }">
              <div class="text-xs text-600">{{ data.description }}</div>
            </template>
          </Column>
          
          <Column header="Action" style="width: 15%">
            <template #body="{ data }">
              <Button 
                icon="pi pi-play" 
                size="small" 
                @click="selectTool(data)"
                severity="primary"
                class="p-button-sm"
                text
                rounded
              />
            </template>
          </Column>
        </DataTable>
      </div>
      
      <div v-else class="text-center p-3">
        <i class="pi pi-info-circle text-2xl text-500"></i>
        <p class="text-500 text-sm mt-2">No tools available for this persona</p>
      </div>
    </Dialog>

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

/* Real-time status display */
.real-time-status {
  border-left: 4px solid var(--primary-color);
  background: var(--surface-50);
}

.llm-status, .tool-status {
  font-size: 0.875rem;
}

.llm-status .pi-spinner {
  animation: spin 1s linear infinite;
}

.tool-status .pi-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
