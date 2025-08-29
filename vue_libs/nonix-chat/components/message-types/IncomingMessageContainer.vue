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
</style>


