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

const emit = defineEmits(['sendMessage', 'regenerateResponse', 'showTools']);

// Service injection
const chatService = inject('chat-runtime');

// State management - session-specific
const messages = ref([]);
const inputText = ref('');
const loading = ref(false);

// Session-specific input text storage
const sessionInputTexts = ref(new Map());

// Register all message types with the manager
onMounted(() => {
  chatMessageTypeManager.registerMessageType('text', TextMessage);
  chatMessageTypeManager.registerMessageType('system', SystemMessage);
  chatMessageTypeManager.registerMessageType('tool', ToolMessage);
  chatMessageTypeManager.registerMessageType('user', UserMessage);
});

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
  console.log('ChatMessageContainer - selectedSession changed:', newSession);
  console.log('ChatMessageContainer - historyId:', props.historyId);
  
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
      console.log('Loading messages for history:', props.historyId);
      loadMessages(props.historyId);
    } else {
      console.log('No historyId available for message loading');
    }
    
    console.log('Selected session changed:', newSession);
  }
}, { immediate: true });

// Load messages for specific history
const loadMessages = async (historyId) => {
  console.log('loadMessages called with historyId:', historyId);
  if (!historyId || !chatService) {
    console.log('loadMessages early return - historyId:', historyId, 'chatService:', !!chatService);
    return;
  }
  
  try {
    loading.value = true;
    console.log('Calling chatService.getHistoryMessages with:', historyId);
    const response = await chatService.getHistoryMessages(historyId);
    console.log('Messages response:', response);
    
    // Handle different response structures
    if (response.data && Array.isArray(response.data)) {
      messages.value = response.data;
    } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
      messages.value = response.data.data;
    } else if (Array.isArray(response)) {
      messages.value = response;
    } else {
      messages.value = [];
    }
    
    console.log('Final messages value:', messages.value);
    
    // Debug: Log individual message details
    if (messages.value.length > 0) {
      console.log('First message details:', messages.value[0]);
      console.log('Message structure:', {
        id: messages.value[0].id,
        message_type: messages.value[0].message_type,
        content: messages.value[0].content,
        content_json: messages.value[0].content_json,
        role: messages.value[0].role,
        timestamp: messages.value[0].timestamp
      });
    }
  } catch (error) {
    console.error('Failed to load messages:', error);
    messages.value = [];
  } finally {
    loading.value = false;
  }
};

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

// Show tools
const showTools = () => {
  emit('showTools');
};

// Get the appropriate component for each message
const getMessageComponent = (message) => {
  const messageType = message.message_type || 'text';
  console.log('Getting component for message type:', messageType, 'message:', message);
  const component = chatMessageTypeManager.getMessageType(messageType);
  console.log('Returned component:', component);
  return component;
};

// Check if message has a valid type
const hasValidMessageType = (message) => {
  const messageType = message.message_type || 'text';
  const hasType = chatMessageTypeManager.hasMessageType(messageType);
  console.log('Message type validation:', messageType, 'hasType:', hasType);
  return hasType;
};

// Computed values
const hasHistory = computed(() => !!props.historyId);
const canSendMessage = computed(() => hasHistory.value && inputText.value?.trim());
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
        <!-- Debug info for each message -->
        <div class="p-2 surface-200 text-xs mb-1">
          Debug: ID={{ message.id }}, Type={{ message.message_type || 'undefined' }}, Role={{ message.role }}, Content={{ message.content || message.content_json || 'no content' }}
        </div>
        
        <component
          :is="getMessageComponent(message)"
          v-if="hasValidMessageType(message)"
          :message="message"
          :currentUserId="currentUserId"
        />
        <div v-else class="p-3 text-center text-color-secondary">
          <i class="pi pi-exclamation-triangle mr-2"></i>
          Unknown message type: {{ message.message_type || 'undefined' }}
        </div>
      </div>
    </div>

    <!-- Message Input Area -->
    <div class="flex align-items-center p-1 border-top-1 surface-border surface-section flex-shrink-0">
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
      <div class="flex align-items-center gap-2">
        <Button 
          icon="pi pi-ellipsis-h" 
          text 
          rounded 
          severity="secondary"
          :disabled="!hasHistory"
        />
      </div>
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
