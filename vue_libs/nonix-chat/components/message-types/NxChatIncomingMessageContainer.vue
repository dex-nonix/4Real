<script setup>
import {computed, ref} from 'vue';
import Button from 'primevue/button';
import Menu from 'primevue/menu';

const props = defineProps({
  message: {type: Object, required: true},
  component: {type: Object, required: true},
  currentUserId: {type: [String, Number], required: false},
  editingMessageId: {type: [String, Number], default: null},
  sessionId: {type: [String, Number], required: true},
  historyId: {type: [String, Number], required: true}
})

const emit = defineEmits(['delete-message', 'copy', 'stop', 'start-edit', 'cancel-edit', 'edit-success'])

// Simple menu system
const messageActions = ref({});
const menu = ref();

// Handle actions registration from child components
const handleRegisterActions = (actions) => {
  messageActions.value = actions;
};

// Create menu items from registered actions
const menuItems = computed(() => {
  return Object.entries(messageActions.value).map(([key, action]) => ({
    label: action.label,
    icon: action.icon,
    command: () => handleAction(key)
  }));
});

// Handle action execution
const handleAction = (actionKey, extraData = {}) => {
  switch (actionKey) {
    case 'copy':
      // Extract message content for copy
      let content = '';
      if (props.message.content_json?.text) {
        content = props.message.content_json?.text;
      } else if (props.message.content) {
        content = props.message.content;
      }
      emit('copy', {messageId: props.message.id, content});
      break;
    case 'edit':
      emit('start-edit', props.message.id);
      break;
    case 'delete':
      emit('delete-message', {messageId: props.message.id});
      break;
    case 'stop':
      emit('stop', props.message.id);
      break;
  }
};

// Simple menu toggle
const toggleMenu = (event) => {
  menu.value.toggle(event);
};
</script>

<template>
  <!-- AI Message Container -->
  <div class="message-container">

    <!-- Actions Button -->
    <div v-if="Object.keys(messageActions).length > 0" class="message-actions">
      <Button
          icon="pi pi-ellipsis-h"
          text
          severity="secondary"
          size="small"
          @click="toggleMenu"
          class="action-button"
      />
      <Menu ref="menu" :model="menuItems" :popup="true"/>
    </div>

    <!-- Message Content -->
    <div class="flex align-items-start message-content-wrapper">
      <component
          :is="component"
          :message="message"
          :current-user-id="currentUserId"
          :editing-message-id="editingMessageId"
          :session-id="sessionId"
          :history-id="historyId"
          @register-actions="handleRegisterActions"
          @edit-success="$emit('edit-success')"
          @cancel-edit="$emit('cancel-edit')"
      />
    </div>
  </div>
</template>

<style scoped>
/* Message Container */
.message-container {
  position: relative;
  margin-bottom: 0.5rem;
}

/* Message Content Wrapper */
.message-content-wrapper {
  background: var(--surface-section);
  border: 2px solid var(--surface-border);
  border-left: 4px solid var(--blue-500);
  border-radius: 12px;
  padding: 1rem;
}

/* Actions */
.message-actions {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  z-index: 10;
}

/* Action Button */
.action-button {
  width: 20px !important;
  height: 20px !important;
  padding: 2px !important;
  background: transparent !important;
  border: none !important;
}
</style>


