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

const menu = ref();
const selectedMessage = ref(null);
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
    console.log('Delete:', selectedMessage.value);
    // Emit delete event for parent component to handle
};

// Handle different field names from API
const messageContent = computed(() => props.message.content || props.message.content_json || props.message.text || 'No content');
</script>

<template>
  <!-- Text message content only - outer styling handled by MessageContainer -->
  <div class="flex align-items-start">
    <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">{{ messageContent }}</p>
    <Button
      icon="pi pi-ellipsis-v"
      text rounded severity="secondary"
      class="p-button-sm ml-2 flex-shrink-0"
      @click="toggleMenu($event, message)"
    />
  </div>
  
  <Menu ref="menu" :model="menuItems" :popup="true" />
</template>
