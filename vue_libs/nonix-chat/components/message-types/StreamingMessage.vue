<!-- StreamingMessage.vue -->
<script setup>
import { ref, onMounted, onUnmounted, inject, computed } from 'vue';
import Button from 'primevue/button';
import Menu from 'primevue/menu';
import ProgressSpinner from 'primevue/progressspinner';

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

const emit = defineEmits(['deleteMessage']);

const streamingContent = ref('');
const streamingStatus = ref('streaming');
const isTyping = ref(true);
const typingDots = ref('...');
const menu = ref();
const selectedMessage = ref(null);
const showDeleteConfirm = ref(false);
const isDeleting = ref(false);

const chatService = inject('chat-service');

const menuItems = ref([
    { label: 'Copy', icon: 'pi pi-copy', command: () => handleCopy() },
    { label: 'Edit', icon: 'pi pi-pencil', command: () => handleEdit() },
    { separator: true },
    { label: 'Delete', icon: 'pi pi-trash', command: () => handleDelete() }
]);

let typingInterval;
const startTypingAnimation = () => {
  typingInterval = setInterval(() => {
    if (typingDots.value === '...') {
      typingDots.value = '';
    } else {
      typingDots.value += '.';
    }
  }, 500);
};

const stopTypingAnimation = () => {
  if (typingInterval) {
    clearInterval(typingInterval);
    typingInterval = null;
  }
};

const handleAssistantChunk = (data) => {
  if (data.message_id === props.message.id) {
    streamingContent.value += data.chunk;
    console.log(`StreamingMessage ${props.message.id}: Chunk received, content length: ${streamingContent.value.length}`);
  }
};

const handleAssistantComplete = (data) => {
  if (data.message_id === props.message.id) {
    streamingStatus.value = 'complete';
    isTyping.value = false;
    stopTypingAnimation();
    console.log(`StreamingMessage ${props.message.id}: Streaming complete`);
  }
};

const handleStreamingError = (data) => {
  if (data.message_id === props.message.id) {
    streamingStatus.value = 'error';
    isTyping.value = false;
    stopTypingAnimation();
    console.error(`StreamingMessage ${props.message.id}: Streaming error:`, data.error_message);
  }
};

onMounted(() => {
  if (chatService) {
    const unsubscribeChunk = chatService.onWebSocketEvent('assistant_message_chunk', handleAssistantChunk);
    const unsubscribeComplete = chatService.onWebSocketEvent('assistant_message_complete', handleAssistantComplete);
    const unsubscribeError = chatService.onWebSocketEvent('streaming_error', handleStreamingError);
    
    startTypingAnimation();
    
    props.message._unsubscribe = () => {
      unsubscribeChunk();
      unsubscribeComplete();
      unsubscribeError();
    };
  }
});

onUnmounted(() => {
  stopTypingAnimation();
  if (props.message._unsubscribe) {
    props.message._unsubscribe();
  }
});

const toggleMenu = (event, message) => {
    selectedMessage.value = message;
    menu.value.toggle(event);
};

const handleCopy = () => {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(streamingContent.value);
    }
    console.log('Copy:', selectedMessage.value);
};

const handleEdit = () => {
    console.log('Edit:', selectedMessage.value);
    // Emit edit event for parent component to handle
};

const handleDelete = () => {
    selectedMessage.value = props.message;
    showDeleteConfirm.value = true;
    menu.value.hide();
};

const confirmDelete = async () => {
    if (!selectedMessage.value) return;
    
    try {
        isDeleting.value = true;
        emit('deleteMessage', {
            messageId: selectedMessage.value.id,
            historyId: selectedMessage.value.history_id,
            content: streamingContent.value
        });
        showDeleteConfirm.value = false;
        selectedMessage.value = null;
    } catch (error) {
        console.error('Delete failed:', error);
    } finally {
        isDeleting.value = false;
    }
};

const cancelDelete = () => {
    showDeleteConfirm.value = false;
    selectedMessage.value = null;
};

const displayContent = computed(() => {
  if (streamingStatus.value === 'complete') {
    return streamingContent.value || 'No content';
  }
  return streamingContent.value || '';
});

const isStreaming = computed(() => streamingStatus.value === 'streaming');
const hasError = computed(() => streamingStatus.value === 'error');
</script>

<template>
  <div class="flex align-items-start">
    <div class="flex-grow-1">
      <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">
        {{ displayContent }}
        
        <span v-if="isStreaming && isTyping" class="typing-indicator">
          <span class="typing-dots">{{ typingDots }}</span>
        </span>
      </p>
      
      <div v-if="isStreaming" class="streaming-status mt-2">
        <div class="flex align-items-center gap-2">
          <ProgressSpinner style="width: 16px; height: 16px;" />
          <span class="text-xs text-warning">AI is typing{{ typingDots }}</span>
        </div>
      </div>
      
      <div v-if="hasError" class="error-status mt-2">
        <div class="flex align-items-center gap-2">
          <i class="pi pi-exclamation-triangle text-danger text-sm"></i>
          <span class="text-xs text-danger">Streaming error occurred</span>
        </div>
      </div>
    </div>
    
    <div v-if="showDeleteConfirm && selectedMessage?.id === message.id" class="flex align-items-center ml-2">
      <span class="text-xs text-red-500 mr-2">Delete?</span>
      <Button
        icon="pi pi-check"
        size="small"
        severity="danger"
        text
        rounded
        :loading="isDeleting"
        @click="confirmDelete"
        class="p-button-sm mr-1"
      />
      <Button
        icon="pi pi-times"
        size="small"
        severity="secondary"
        text
        rounded
        @click="cancelDelete"
        class="p-button-sm"
      />
    </div>
    
    <Button
      v-else
      icon="pi pi-ellipsis-v"
      text rounded severity="secondary"
      class="p-button-sm ml-2 flex-shrink-0"
      @click="toggleMenu($event, message)"
    />
  </div>
  
  <Menu ref="menu" :model="menuItems" :popup="true" />
</template>

<style scoped>
.flex {
  transition: all 0.2s ease;
}

.p-button-sm {
  min-width: 2rem;
  height: 1.5rem;
}

.typing-indicator {
  display: inline-block;
  min-width: 24px;
}

.typing-dots {
  color: var(--text-color-secondary);
  font-weight: bold;
}

.streaming-status {
  opacity: 0.8;
}

.error-status {
  opacity: 0.8;
}

.text-normal {
  transition: all 0.1s ease;
}
</style>
