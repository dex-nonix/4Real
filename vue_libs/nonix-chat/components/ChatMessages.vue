<!-- ChatMessages.vue -->
<!--
  Updated to use ChatMessageTypeManager for dynamic message rendering
  Each message type is now handled by its own component
-->
<script setup>
import { computed, onMounted } from 'vue';
import chatMessageTypeManager from './ChatMessageTypeManager.js';
import TextMessage from './message-types/TextMessage.vue';
import SystemMessage from './message-types/SystemMessage.vue';
import ToolMessage from './message-types/ToolMessage.vue';
import UserMessage from './message-types/UserMessage.vue';

const props = defineProps({
  messages: {
    type: Array,
    required: true,
    default: () => []
  },
  currentUserId: {
    type: [String, Number],
    required: true
  }
});

// Register all message types with the manager
onMounted(() => {
  chatMessageTypeManager.registerMessageType('text', TextMessage);
  chatMessageTypeManager.registerMessageType('system', SystemMessage);
  chatMessageTypeManager.registerMessageType('tool', ToolMessage);
  chatMessageTypeManager.registerMessageType('user', UserMessage);
});

// Get the appropriate component for each message
const getMessageComponent = (message) => {
  const messageType = message.message_type || 'text';
  return chatMessageTypeManager.getMessageType(messageType);
};

// Check if message has a valid type
const hasValidMessageType = (message) => {
  const messageType = message.message_type || 'text';
  return chatMessageTypeManager.hasMessageType(messageType);
};
</script>

<template>
  <div class="flex-1 p-4 overflow-y-auto surface-ground">
    <div v-if="messages.length === 0" class="text-center text-color-secondary p-4">
      <i class="pi pi-comments text-4xl mb-2"></i>
      <p>No messages yet. Start a conversation!</p>
    </div>
    
    <div v-else v-for="message in messages" :key="message.id">
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
</template>