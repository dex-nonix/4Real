<!-- ChatMessageContainer.vue -->
<!--
  Unified message container that combines ChatMessages + ChatMessageInput
  Manages session-specific data and input persistence
-->
<script setup>
import { ref, computed, onMounted, inject, watch } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import chatMessageTypeManager from './ChatMessageTypeManager.js';
import MessageContainer from './message-types/MessageContainer.vue';
import TextMessage from './message-types/TextMessage.vue';
import SystemMessage from './message-types/SystemMessage.vue';
import ToolMessage from './message-types/ToolMessage.vue';
import UserMessage from './message-types/UserMessage.vue';

const props = defineProps({
  sessionId: { type: [String, Number, null], required: true },
  historyId: { type: [String, Number, null], required: false, default: null },
  currentUserId: { type: [String, Number], required: true, default: 'user-self' },
  selectedSession: { type: Object, required: false, default: null },
  availableTools: { type: Array, default: () => [] }
});

const emit = defineEmits(['sendMessage', 'regenerateResponse', 'error', 'deleteMessage']);

// Service injection
const chatService = inject('chat-service');

// State management - session-specific
const messages = ref([]);
const inputText = ref('');
const loading = ref(false);


// Toggle for mockup vs real data
const useMockupData = ref(true); // Start with mockup data to ensure messages are visible

// Watch for toggle changes to reload messages
watch(useMockupData, (newValue) => {
  if (props.historyId || newValue) {
    loadMessages(props.historyId);
  }
});

// Session-specific input text storage
const sessionInputTexts = ref(new Map());

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
    // First get the session ID from the selectedSession prop
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

// Trigger refresh from parent
const triggerRefresh = async () => {
  await loadMessages(props.historyId);
};

// Load messages when historyId changes
watch(() => props.historyId, async (newHistoryId, oldHistoryId) => {
  if (newHistoryId) {
    // Clear existing messages before loading new ones
    messages.value = [];
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

// Expose methods for parent component
defineExpose({
  loadMessages,
  clearLocalMessages,
  refreshMessages: () => loadMessages(props.historyId),
  triggerRefresh: triggerRefresh
});
</script>

<template>
  <div class="flex flex-column flex-1" style="min-height: 0;">
    <!-- Messages Display Area -->
    <div class="flex-1 p-4 overflow-y-auto surface-ground">
      <div v-if="loading" class="text-center p-4">
        <i class="pi pi-spin pi-spinner text-2xl"></i>
        <p class="mt-2">Loading messages...</p>
      </div>
      
      <div v-else-if="messages.length === 0" class="text-center text-color-secondary p-4">
        <i class="pi pi-comments text-4xl mb-2"></i>
        <p>No messages yet. Start a conversation!</p>
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
        
        <div v-else class="p-3 text-center text-color-secondary">
          <i class="pi pi-exclamation-triangle mr-2"></i>
          Unknown message type: {{ message.message_type || 'undefined' }}
        </div>
      </div>
    </div>

    <!-- Message Input Area -->
    <div class="flex align-items-center p-1 border-top-1 surface-border surface-section flex-shrink-0">
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
    </div>
  </div>
</template>

<style scoped>
/* Ensure proper flexbox behavior */
.flex-1 {
  flex: 1 1 auto;
}

/* Message area scrolling */
.overflow-y-auto {
  overflow-y: auto;
}

/* Input area stays at bottom */
.flex-shrink-0 {
  flex-shrink: 0;
}
</style>
