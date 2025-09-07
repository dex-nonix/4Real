<!-- MessageContainer.vue -->
<!-- Generic message wrapper that handles all outer styling and layout -->
<script setup>
import { computed } from 'vue';

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: [String, Number],
    required: true
  }
});

// Handle different field names from API
const messageSenderId = computed(() => props.message.senderId || props.message.role || '');
const messageTimestamp = computed(() => props.message.timestamp || props.message.created_at || '');
// Treat any role === 'user' as own message for alignment purposes
const isOwnMessage = computed(() => props.message?.role === 'user' || messageSenderId.value === props.currentUserId);

// Message type styling
const getMessageTypeIcon = (messageType) => {
  switch (messageType) {
    case 'text': return 'pi pi-comment';
    case 'system': return 'pi pi-info-circle';
    case 'tool': return 'pi pi-cog';
    case 'user': return 'pi pi-user';
    default: return 'pi pi-message';
  }
};

const getMessageTypeColor = (messageType) => {
  switch (messageType) {
    case 'text': return 'text-primary';
    case 'system': return 'text-info';
    case 'tool': return 'text-warning';
    case 'user': return 'text-success';
    default: return 'text-secondary';
  }
};
</script>

<template>
  <div class="flex mb-4" :class="isOwnMessage ? 'justify-content-end' : 'justify-content-start'">
    <div class="flex flex-column" style="max-width: 80%;">
      
      <!-- Message Card Container -->
      <div
        class="p-3 border-round-xl shadow-1 message-card"
        :class="{
          'ai-message': !isOwnMessage,
          'user-message': isOwnMessage
        }"
      >
        <!-- Message Content Slot -->
        <div class="message-content">
          <slot name="content"></slot>
        </div>
      </div>
      
      <!-- Timestamp and Status -->
      <div
        class="flex align-items-center mt-1 px-2"
        :class="{
          'justify-content-end': isOwnMessage,
          'justify-content-start': !isOwnMessage
        }"
      >
        <span class="text-xs text-400">{{ messageTimestamp }}</span>
        
        <!-- Message Status Indicators -->
        <div v-if="isOwnMessage" class="ml-2">
          <i v-if="message.status === 'sent'" class="pi pi-check text-500 text-sm"></i>
          <i v-if="message.status === 'delivered'" class="pi pi-check-circle text-500 text-sm"></i>
          <i v-if="message.status === 'pending'" class="pi pi-clock text-500 text-sm"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-content {
  /* Ensure content takes full width of card */
  width: 100%;
}

/* Message card hover effects */
.message-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
