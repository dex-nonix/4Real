<!-- TextMessage.vue -->
<script setup>
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
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
const messageTimestamp = computed(() => props.message.timestamp || props.message.created_at || '');
const messageSenderId = computed(() => props.message.senderId || props.message.role || '');
const isOwnMessage = computed(() => messageSenderId.value === props.currentUserId);
</script>

<template>
  <div class="flex mb-4" :class="isOwnMessage ? 'justify-content-end' : 'justify-content-start'">
    <div class="flex flex-column" style="max-width: 80%;">
      <div
          class="p-3 text-color-secondary border-round-xl"
          :class="{
              'surface-card shadow-1': isOwnMessage,
              'surface-200': !isOwnMessage
          }"
      >
        <div class="flex align-items-start">
          <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">{{ messageContent }}</p>
          <Button
            icon="pi pi-ellipsis-v"
            text rounded severity="secondary"
            class="p-button-sm ml-2 flex-shrink-0"
            @click="toggleMenu($event, message)"
          />
        </div>
      </div>

      <div
        class="flex align-items-center mt-1 px-2"
        :class="{
          'justify-content-end': isOwnMessage,
          'justify-content-start': !isOwnMessage
        }"
      >
         <span class="text-xs text-color-secondary">{{ messageTimestamp }}</span>
         <i v-if="isOwnMessage && message.status === 'sent'" class="pi pi-check ml-1 text-color-secondary text-sm"></i>
         <i v-if="isOwnMessage && message.status === 'delivered'" class="pi pi-check-circle ml-1 text-color-secondary text-sm"></i>
         <ProgressSpinner
            v-if="isOwnMessage && message.status === 'pending'"
            style="width: 14px; height: 14px"
            strokeWidth="8"
            class="ml-1"
          />
      </div>
    </div>
    <Menu ref="menu" :model="menuItems" :popup="true" />
  </div>
</template>
