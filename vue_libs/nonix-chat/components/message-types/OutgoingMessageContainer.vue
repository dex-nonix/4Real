<script setup>
const props = defineProps({
  message: { type: Object, required: true },
  component: { type: Object, required: true },
  currentUserId: { type: [String, Number], required: false }
})

const emit = defineEmits(['delete-message', 'copy', 'retry', 'cancel'])
</script>

<template>
  <div class="flex flex-column gap-1">
    <div class="flex align-items-center justify-content-between">
      <div class="text-xs text-400">{{ message.created_at }}</div>
      <div class="flex align-items-center gap-1">
        <button v-if="message.status==='sending'" class="p-button p-button-text p-button-rounded p-button-danger p-button-sm" @click="$emit('cancel', message.id)">
          <i class="pi pi-times"></i>
        </button>
        <button v-if="message.status==='error'" class="p-button p-button-text p-button-rounded p-button-warning p-button-sm" @click="$emit('retry', message.id)">
          <i class="pi pi-refresh"></i>
        </button>
        <button class="p-button p-button-text p-button-rounded p-button-sm" @click="$emit('copy', message.id)">
          <i class="pi pi-copy"></i>
        </button>
        <button class="p-button p-button-text p-button-rounded p-button-sm" @click="$emit('delete-message', { messageId: message.id })">
          <i class="pi pi-trash"></i>
        </button>
      </div>
    </div>
    <component :is="component" :message="message" :currentUserId="currentUserId" />
  </div>
</template>

<style scoped>
</style>


