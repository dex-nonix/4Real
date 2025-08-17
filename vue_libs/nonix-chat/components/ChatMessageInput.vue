<!-- ChatMessageInput.vue -->
<script setup>
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';

const message = defineModel();

const props = defineProps({
  currentHistoryId: { type: [String, Number, null], required: false, default: null },
  availableTools: { type: Array, default: () => [] }
});

const emit = defineEmits(['sendMessage', 'regenerateResponse', 'showTools']);

const onSend = () => {
  if (message.value?.trim() && props.currentHistoryId) {
    emit('sendMessage', message.value);
    message.value = '';
  }
};

const showTools = () => {
  emit('showTools');
};
</script>

<template>
  <div class="flex align-items-center p-1 border-top-1 surface-border surface-section flex-shrink-0">
    <!-- Has to open a Popup menu(not dialog) to show the menu points to choose from optionally with submenu! -->
    <!-- also a menu item for the tools and mcp info(dialog to manage in own file each for tools, one for MCP) -->
    <Button 
      icon="pi pi-box" 
      text 
      rounded 
      severity="secondary"
      @click="showTools"
      v-tooltip.bottom="'Available Tools'"
      :disabled="!currentHistoryId"
    />

    <span class="p-input-icon-right flex-grow-1 mx-2">
      <IconField>
        <InputText
          v-model="message"
          placeholder="Type a message..."
          class="w-full"
          @keyup.enter="onSend"
          :disabled="!currentHistoryId"
        />
        <InputIcon class="pi pi-send" @click="onSend" />
      </IconField>
    </span>

    <div class="flex align-items-center gap-2">
      <!-- open an options dialog for more options -->
      <Button icon="pi pi-ellipsis-h" text rounded severity="secondary"/>
    </div>
  </div>
</template>