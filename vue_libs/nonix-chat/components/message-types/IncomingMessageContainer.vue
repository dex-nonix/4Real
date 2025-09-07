<script setup>
import BackendMessage from './BackendMessage.vue'

const props = defineProps({
  message: { type: Object, required: true },
  component: { type: Object, required: true },
  currentUserId: { type: [String, Number], required: false }
})

const emit = defineEmits(['delete-message', 'copy', 'stop'])
</script>

<template>
  <BackendMessage :message="message" @delete="$emit('delete-message', { messageId: message.id })" @copy="$emit('copy', message.id)" @stop="$emit('stop', message.id)">
    <component :is="component" :message="message" :currentUserId="currentUserId" />
  </BackendMessage>
</template>

<style scoped>
/* AI Message Container */
:deep(.flex.align-items-start) {
  background: var(--surface-section) !important;
  border: 2px solid var(--surface-border) !important;
  border-left: 4px solid var(--blue-500) !important;
  border-radius: 12px !important;
  padding: 1rem !important;
  transition: all 0.2s ease !important;
}

/* AI Message hover effects */
:deep(.flex.align-items-start:hover) {
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.2) !important;
  transform: translateY(-1px) !important;
}
</style>


