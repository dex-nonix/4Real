<script setup>
import { computed, onMounted, ref, watch, inject } from 'vue';
import MessageEditMode from './MessageEditMode.vue';
import { useMessageEdit } from './useMessageEdit.js';

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
  },
  sessionId: {
    type: [String, Number],
    required: true
  },
  historyId: {
    type: [String, Number],
    required: true
  }
});

const emit = defineEmits(['deleteMessage', 'register-actions', 'cancel-edit', 'edit-success']);

const messageContent = computed(() => props.message?.content_json?.text || '');
const isValid = computed(() => props.message.metadata?.isValid !== false);

// Initialize services
const chatService = inject('chat-service');

// Use the reusable edit composable
const { handleEdit: handleMessageEdit } = useMessageEdit(chatService);
const editContent = ref('');

const isEditing = computed(() => {
  return props.editingMessageId && String(props.editingMessageId) === String(props.message.id);
});

const messageActions = {
  copy: { label: 'Copy', icon: 'pi pi-copy' },
  edit: { label: 'Edit', icon: 'pi pi-pencil' },
  delete: { label: 'Delete', icon: 'pi pi-trash' }
};

// Use the composable's handleEdit function
const handleEdit = (editData) => {
  return handleMessageEdit(editData, props, emit, 'UserMessage');
};

const handleCancelEdit = () => {
  console.info('📝 UserMessage: Canceling edit mode');
  emit('cancel-edit');
};

const handleKeyDown = (event) => {};

watch(() => props.editingMessageId, (newId) => {
  if (newId && String(newId) === String(props.message.id)) {
    editContent.value = messageContent.value;
  }
});

onMounted(() => {
  emit('register-actions', messageActions);
});
</script>

<template>
  <div class="flex align-items-start justify-content-start w-full">
    <MessageEditMode
      v-if="isEditing"
      :model-value="editContent"
      :placeholder="'Edit your message...'"
      :message-id="props.message.id"
      :original-content="messageContent"
      @update:model-value="editContent = $event"
      @edit="handleEdit"
      @cancel-edit="handleCancelEdit"
      @keydown="handleKeyDown"
      class="w-full"
    />

    <div v-else class="display-mode w-full">
      <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">{{ messageContent }}</p>

      <div v-if="props.message.senderId !== props.currentUserId && props.message.role !== props.currentUserId" class="ml-2">
        <i v-if="isValid" class="pi pi-check-circle text-success text-sm"></i>
        <i v-else class="pi pi-exclamation-triangle text-warning text-sm"></i>
      </div>
    </div>
  </div>

  <div v-if="!isValid" class="mt-2">
    <span class="text-xs text-warning">Invalid input</span>
  </div>
</template>

<style scoped>
</style>
