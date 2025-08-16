<!-- ChatMessageInput.vue -->
<script setup>
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';

const message = defineModel();

const emit = defineEmits(['sendMessage', 'regenerateResponse']);

const onSend = () => {
  if (message.value?.trim()) {
    emit('sendMessage', message.value);
    message.value = '';
  }
};
</script>

<template>
  <div class="flex align-items-center p-1 border-top-1 surface-border surface-section flex-shrink-0">
    <!-- Has to open a Popup menu(not dialog) to show  the menu pooiints to choose fronm optiponaly with submenu! o it has to use  normaöl prime menu has to be dined in a own file !!
    also a menu item for the tools and mcp  info(diakig to o manage in a own fole each infor tools, one e for MCP)
    -->
    <Button icon="pi pi-box" text rounded severity="secondary"/>

    <span class="p-input-icon-right flex-grow-1 mx-2">
      <IconField>
            <InputText
                v-model="message"
                placeholder="Type a message..."
                class="w-full"
                @keyup.enter="onSend"
            />
            <InputIcon class="pi pi-send" @click="onSend"/>
        </IconField>
    </span>

    <div class="flex align-items-center gap-2">
      <!-- open an options dialog for more options -->
      <Button icon="pi pi-ellipsis-h" text rounded severity="secondary"/>
    </div>
  </div>
</template>