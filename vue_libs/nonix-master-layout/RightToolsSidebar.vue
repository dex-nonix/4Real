<template>
  <Sidebar
    v-model:visible="visible"
    position="right"
    modal
    :dismissable="true"
    :showCloseIcon="false"
    :header="null"
    :style="{ width: '450px' }"
  >
    <Chat @close-chat="handleChatClose" />
  </Sidebar>
</template>

<script setup>
import Sidebar from 'primevue/sidebar'
import { computed } from 'vue'
import { useAppShell } from './useAppShell.js'
import Chat from '@nonix-chat/components/Chat.vue'

const { state } = useAppShell()
const visible = computed({
  get: () => state.rightOpen,
  set: (v) => { state.rightOpen = v }
})

// Handle chat close event from standalone Chat component
const handleChatClose = () => {
  console.log('Chat close event received - closing sidebar');
  state.rightOpen = false;
}
</script>


