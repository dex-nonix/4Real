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
    <Chat />
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
</script>


