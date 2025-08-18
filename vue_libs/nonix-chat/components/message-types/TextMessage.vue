<!-- TextMessage.vue -->
<script setup>
import Button from 'primevue/button';
import Menu from 'primevue/menu';
import { ref, computed } from 'vue';

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

const menu = ref();
const selectedMessage = ref(null);
const showDeleteConfirm = ref(false);
const isDeleting = ref(false);

const menuItems = ref([
    { label: 'Copy', icon: 'pi pi-copy', command: () => handleCopy() },
    { label: 'Edit', icon: 'pi pi-pencil', command: () => handleEdit() },
    { separator: true },
    { label: 'Delete', icon: 'pi pi-trash', command: () => handleDelete() }
]);

const toggleMenu = (event, message) => {
    selectedMessage.value = message;
    menu.value.toggle(event);
};

const handleCopy = () => {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(messageContent.value);
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
    menu.value.hide(); // Hide the menu
};

const confirmDelete = async () => {
    if (!selectedMessage.value) return;
    
    try {
        isDeleting.value = true;
        emit('deleteMessage', {
            messageId: selectedMessage.value.id,
            historyId: selectedMessage.value.history_id,
            content: messageContent.value
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

// Handle different field names from API
const messageContent = computed(() => props.message.content || props.message.content_json || props.message.text || 'No content');
</script>

<template>
  <!-- Text message content only - outer styling handled by MessageContainer -->
  <div class="flex align-items-start">
    <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">{{ messageContent }}</p>
    
    <!-- Delete Confirmation (Inline) -->
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
    
    <!-- Menu Button -->
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
/* Smooth transitions for delete confirmation */
.flex {
  transition: all 0.2s ease;
}

/* Ensure buttons don't cause layout shifts */
.p-button-sm {
  min-width: 2rem;
  height: 1.5rem;
}
</style>
