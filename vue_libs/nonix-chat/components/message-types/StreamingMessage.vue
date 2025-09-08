<!-- StreamingMessage.vue -->
<script setup>
import { ref, onMounted, onUnmounted, inject, computed, watch } from 'vue';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import { useStreamingMessage } from './useStreamingMessage.js';
import ProgressSpinner from 'primevue/progressspinner';

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: [String, Number],
    required: true
  },
  editingMessageId: {
    type: [String, Number],
    default: null
  }
});

const emit = defineEmits(['deleteMessage', 'register-actions', 'edit', 'cancel-edit']);

const chatService = inject('chat-service');
const { streamingContent, streamingStatus, isTyping, subscribe, unsubscribe, initFromProps } = useStreamingMessage(chatService, props.message, true);
const typingDots = ref('...');

// Define available actions for this message type
const messageActions = {
  copy: { label: 'Copy', icon: 'pi pi-copy' },
  edit: { label: 'Edit', icon: 'pi pi-pencil' },
  delete: { label: 'Delete', icon: 'pi pi-trash' }
};

// Edit mode state
const isEditing = ref(false);
const editContent = ref('');

// Edit functions
const startEdit = () => {
  editContent.value = props.message?.content_json?.text || '';
  isEditing.value = true;
};

const saveEdit = () => {
  if (editContent.value.trim() !== (props.message?.content_json?.text || '')) {
    emit('edit', {
      messageId: props.message.id,
      newContent: editContent.value.trim(),
      originalContent: props.message?.content_json?.text || ''
    });
  }
  isEditing.value = false;
};

const cancelEdit = () => {
  editContent.value = props.message?.content_json?.text || '';
  isEditing.value = false;
  emit('cancel-edit');
};

// Handle keyboard shortcuts
const handleKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    saveEdit();
  } else if (event.key === 'Escape') {
    event.preventDefault();
    cancelEdit();
  }
};

// Watch for editing message ID changes
watch(() => props.editingMessageId, (newId) => {
  if (newId && String(newId) === String(props.message.id)) {
    startEdit();
  } else if (!newId && isEditing.value) {
    cancelEdit();
  }
});

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
  // Register available actions with parent container
  emit('register-actions', messageActions);

  initFromProps();
  // If this message is already finalized, render from persisted content immediately
  if (props.message && props.message.status && props.message.status !== 'streaming') {
    streamingStatus.value = props.message.status;
    isTyping.value = false;
    stopTypingAnimation();
    const finalText = (props.message?.content_json && props.message.content_json.text) || '';
    renderMarkdown(finalText);
    return;
  }
  if (streamingStatus.value === 'streaming') {
    subscribe();
    startTypingAnimation();
  }
});

onUnmounted(() => {
  stopTypingAnimation();
  unsubscribe();
});

// React to parent status changes (e.g., manual Stop)
watch(() => props.message.status, (val) => {
  const next = val || 'streaming';
  streamingStatus.value = next;
  if (next !== 'streaming') {
    isTyping.value = false;
    unsubscribe();
    const finalText = (props.message?.content_json && props.message.content_json.text) || streamingContent.value || '';
    renderMarkdown(finalText);
  }
});

// Menu and action handling is now done by parent container

const displayContent = computed(() => {
  if (streamingStatus.value !== 'streaming') {
    return (props.message?.content_json && props.message.content_json.text) || streamingContent.value || '';
  }
  return streamingContent.value || '';
});

const isStreaming = computed(() => streamingStatus.value === 'streaming');
const hasError = computed(() => streamingStatus.value === 'error');

// Markdown rendering
const renderedHtml = ref('');
let markedRenderer = null;

const renderMarkdown = async (text) => {
  const src = text || '';
  try {
    if (!markedRenderer) {
      try {
        const mod = await import('marked');
        markedRenderer = mod.marked || mod.default || null;
      } catch (_) {
        markedRenderer = null;
      }
    }
    if (markedRenderer) {
      renderedHtml.value = markedRenderer.parse ? markedRenderer.parse(src) : markedRenderer(src);
    } else {
      renderedHtml.value = src.replace(/\n/g, '<br/>');
    }
  } catch (_) {
    renderedHtml.value = src.replace(/\n/g, '<br/>');
  }
};

watch(displayContent, (val) => {
  renderMarkdown(val);
}, { immediate: true });
</script>

<template>
  <div class="flex align-items-start">
    <div class="flex-grow-1">
      <!-- Edit Mode -->
      <div v-if="isEditing" class="edit-mode">
        <Textarea
          v-model="editContent"
          class="edit-textarea"
          :autoResize="true"
          rows="3"
          @keydown="handleKeyDown"
          placeholder="Edit message content..."
        />
        <div class="edit-actions mt-3 flex justify-content-end gap-2">
          <Button
            icon="pi pi-times"
            label="Cancel"
            size="small"
            severity="secondary"
            text
            @click="cancelEdit"
            class="p-button-sm"
          />
          <Button
            icon="pi pi-check"
            label="Save"
            size="small"
            severity="success"
            @click="saveEdit"
            class="p-button-sm"
          />
        </div>
      </div>

      <!-- Display Mode -->
      <div v-else class="display-mode">
        <div class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">
          <div v-html="renderedHtml"></div>
          <span v-if="isStreaming && isTyping" class="typing-indicator">
            <span class="typing-dots">{{ typingDots }}</span>
          </span>
        </div>

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
    </div>
  </div>
</template>

<style scoped>
.flex {
  transition: all 0.2s ease;
}

/* Edit Mode Styling */
.edit-mode {
  padding: 0.5rem;
  background: var(--surface-section);
  border-radius: 8px;
  border: 1px solid var(--surface-border);
}

.edit-textarea {
  width: 100%;
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.5;
  border-radius: 6px;
  border: 1px solid var(--surface-border);
  background: var(--surface-ground);
  color: var(--text-color);
  padding: 0.75rem;
  resize: vertical;
}

.edit-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 1px var(--primary-color);
}

.edit-actions {
  border-top: 1px solid var(--surface-border);
  padding-top: 0.75rem;
}

.edit-actions .p-button {
  min-width: 80px;
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
}

.edit-actions .p-button.p-button-success {
  background: var(--green-500);
  border-color: var(--green-500);
}

.edit-actions .p-button.p-button-success:hover {
  background: var(--green-600);
  border-color: var(--green-600);
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
