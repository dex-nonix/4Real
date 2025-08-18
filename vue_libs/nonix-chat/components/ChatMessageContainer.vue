<script setup>
import { ref, computed, onMounted, inject, watch } from 'vue';
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

// Session-specific input text storage
const sessionInputTexts = ref(new Map());

// Tools state
const showToolsDialog = ref(false);
const availableTools = ref([]);
const toolsLoading = ref(false);

// Register all message types with the manager
onMounted(() => {
  chatMessageTypeManager.registerMessageType('text', TextMessage);
  chatMessageTypeManager.registerMessageType('system', SystemMessage);
  chatMessageTypeManager.registerMessageType('tool', ToolMessage);
  chatMessageTypeManager.registerMessageType('user', UserMessage);
});

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
  console.log('🔧 showTools called');
  console.log('🔧 props.selectedSession:', props.selectedSession);
  console.log('🔧 props.selectedSession?.persona_id:', props.selectedSession?.persona_id);
  console.log('🔧 chatService available:', !!chatService);
  
  try {
    toolsLoading.value = true;
    showToolsDialog.value = true;
    
    // Load tools for the current persona
    if (props.selectedSession?.persona_id && chatService) {
      console.log('🔧 Calling chatService.personaTools with persona_id:', props.selectedSession.persona_id);
      const toolsData = await chatService.personaTools(props.selectedSession.persona_id);
      console.log('🔧 Tools data received:', toolsData);
      
      // Backend returns {data: Array} - extract the actual tools array
      let toolsArray = [];
      if (toolsData && toolsData.data && Array.isArray(toolsData.data)) {
        toolsArray = toolsData.data;
      } else if (Array.isArray(toolsData)) {
        toolsArray = toolsData;
      }
      
      availableTools.value = toolsArray;
      console.log('🔧 Final availableTools:', availableTools.value);
    } else {
      console.log('🔧 No persona_id or chatService, setting empty tools');
      availableTools.value = [];
    }
  } catch (error) {
    console.error('🔧 Failed to load tools:', error);
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
      null // message_id is optional
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
      :style="{ width: '600px' }"
    >
      <div v-if="availableTools.length > 0" class="tools-list">
        <div v-for="tool in availableTools" :key="tool" class="tool-item p-3 surface-100 border-round mb-2">
          <div class="flex align-items-center gap-3">
            <i class="pi pi-wrench text-primary"></i>
            <div class="flex-1">
              <span class="font-mono text-sm">{{ tool }}</span>
            </div>
            <Button 
              icon="pi pi-play" 
              size="small" 
              @click="executeTool(tool)"
              :label="'Execute'"
              severity="primary"
            />
          </div>
        </div>
      </div>
      <div v-else class="text-center p-4">
        <i class="pi pi-info-circle text-2xl text-500 mb-2"></i>
        <p class="text-500">No tools available for this persona</p>
      </div>
    </Dialog>
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
</style>
