<script setup>
import { ref, computed, onMounted, inject, nextTick } from 'vue';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Menu from 'primevue/menu';
import Badge from 'primevue/badge';
import ErrorDialog from './ErrorDialog.vue';
import MessageContainer from './message-types/MessageContainer.vue';
import TextMessage from './message-types/TextMessage.vue';
import SystemMessage from './message-types/SystemMessage.vue';
import ToolMessage from './message-types/ToolMessage.vue';
import UserMessage from './message-types/UserMessage.vue';
import chatMessageTypeManager from './ChatMessageTypeManager.js';

const props = defineProps({
  sessionId: { type: [String, Number], required: true },
  historyId: { type: [String, Number], required: true },
  currentUserId: { type: String, required: true },
  selectedSession: { type: Object, required: true },
  errors: { type: Array, required: false, default: () => [] }
});

const emit = defineEmits(['send-message', 'delete-message', 'refresh-messages', 'error', 'delete-error', 'clear-all-errors', 'copy-error', 'showTools']);

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

// Error handling methods - emit to parent
const deleteError = (errorId) => {
  emit('delete-error', errorId);
};

const clearAllErrors = () => {
  emit('clear-all-errors');
};

const copyError = (error) => {
  emit('copy-error', error);
};

// State management - session-specific
const messages = ref([]);
const inputText = ref('');
const loading = ref(false);
const hasHistory = computed(() => !!props.historyId);

// Session input text storage
const sessionInputTexts = new Map();

// Register all message types with the manager
onMounted(() => {
  chatMessageTypeManager.registerMessageType('text', TextMessage);
  chatMessageTypeManager.registerMessageType('system', SystemMessage);
  chatMessageTypeManager.registerMessageType('tool', ToolMessage);
  chatMessageTypeManager.registerMessageType('user', UserMessage);
});

// Load messages for a specific history
const loadMessages = async (historyId) => {
  if (!historyId || !chatService) return;
  
  try {
    loading.value = true;
    const response = await chatService.getHistoryMessages(props.sessionId, historyId);
    
    if (response && response.data) {
      messages.value = response.data;
    } else {
      messages.value = [];
    }
  } catch (error) {
    console.error('Failed to load messages:', error);
    messages.value = [];
    emit('error', { message: 'Failed to load messages', details: error });
  } finally {
    loading.value = false;
  }
};

// Load messages on mount
onMounted(async () => {
  if (props.historyId) {
    await loadMessages(props.historyId);
  }
});

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
      sessionInputTexts.set(props.selectedSession.id, inputText.value);
    }
    
    // Emit event for parent component
    emit('send-message', messageData);
    
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
      emit('delete-message', { success: true, messageData, response });
    }
  } catch (error) {
    console.error('Failed to delete message:', error);
    // Emit error to parent for toast notification
    emit('delete-message', { success: false, messageData, error });
  }
};

// Show tools
const showTools = () => {
  emit('showTools');
};

// Clear local messages (for when backend clears them)
const clearLocalMessages = () => {
  messages.value = [];
};

// Get the appropriate component for each message
const getMessageComponent = (message) => {
  return chatMessageTypeManager.getComponent(message.type);
};

// Check if message has valid type
const hasValidMessageType = (message) => {
  return chatMessageTypeManager.hasValidType(message.type);
};

// Computed values
const canSendMessage = computed(() => hasHistory.value && inputText.value?.trim());

// Expose methods for parent component
defineExpose({
  loadMessages,
  clearLocalMessages
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
      @delete-error="deleteError"
      @clear-all="clearAllErrors"
      @copy-error="copyError"
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
</style>
