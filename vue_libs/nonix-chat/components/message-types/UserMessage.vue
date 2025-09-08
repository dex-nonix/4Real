<!-- UserMessage.vue -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';

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

// Single canonical source: message.content_json.text
const messageContent = computed(() => props.message?.content_json?.text || '');
const isValid = computed(() => props.message.metadata?.isValid !== false);

// Edit mode state
const isEditing = ref(false);
const editContent = ref('');

// Define available actions for this message type
const messageActions = {
  copy: { label: 'Copy', icon: 'pi pi-copy' },
  edit: { label: 'Edit', icon: 'pi pi-pencil' },
  delete: { label: 'Delete', icon: 'pi pi-trash' }
};

// Edit functions
const startEdit = () => {
  editContent.value = messageContent.value;
  isEditing.value = true;
};

const saveEdit = () => {
  if (editContent.value.trim() !== messageContent.value) {
    emit('edit', {
      messageId: props.message.id,
      newContent: editContent.value.trim(),
      originalContent: messageContent.value
    });
  }
  isEditing.value = false;
};

const cancelEdit = () => {
  editContent.value = messageContent.value;
  isEditing.value = false;
  // Emit event to clear editing state in parent
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

onMounted(() => {
  // Register available actions with parent container
  emit('register-actions', messageActions);
});
</script>

<template>
  <!-- User message content only - outer styling handled by MessageContainer -->

  <!-- No header/avatar for user messages -->

  <!-- Message Content -->
  <div class="flex align-items-start justify-content-start">
    <!-- Edit Mode -->
    <div v-if="isEditing" class="edit-mode">
      <Textarea
        v-model="editContent"
        class="edit-textarea"
        :autoResize="true"
        rows="2"
        @keydown="handleKeyDown"
        placeholder="Edit your message..."
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
      <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">{{ messageContent }}</p>

      <!-- Validation Indicator -->
      <div v-if="props.message.senderId !== props.currentUserId && props.message.role !== props.currentUserId" class="ml-2">
        <i v-if="isValid" class="pi pi-check-circle text-success text-sm"></i>
        <i v-else class="pi pi-exclamation-triangle text-warning text-sm"></i>
      </div>
    </div>
  </div>

  <!-- Input Validation Status -->
  <div v-if="!isValid" class="mt-2">
    <span class="text-xs text-warning">Invalid input</span>
  </div>
</template>

<style scoped>
/* Edit Mode Styling */
.edit-mode {
  padding: 0.5rem;
  background: var(--surface-section);
  border-radius: 8px;
  border: 1px solid var(--surface-border);
  width: 100%;
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
</style>
