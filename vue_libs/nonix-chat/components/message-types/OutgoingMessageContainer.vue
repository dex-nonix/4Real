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
    <div class="flex align-items-center justify-content-end">
      <div class="flex align-items-center gap-0 message-actions">
        <button v-if="message.status==='sending'" class="p-button p-button-text p-button-rounded p-button-danger p-button-xs" @click="$emit('cancel', message.id)">
          <i class="pi pi-times"></i>
        </button>
        <button v-if="message.status==='error'" class="p-button p-button-text p-button-rounded p-button-warning p-button-xs" @click="$emit('retry', message.id)">
          <i class="pi pi-refresh"></i>
        </button>
        <button class="p-button p-button-text p-button-rounded p-button-xs" @click="$emit('copy', message.id)">
          <i class="pi pi-copy"></i>
        </button>
        <button class="p-button p-button-text p-button-rounded p-button-xs" @click="$emit('delete-message', { messageId: message.id })">
          <i class="pi pi-trash"></i>
        </button>
      </div>
    </div>
    <component :is="component" :message="message" :currentUserId="currentUserId" />
  </div>
</template>

<style scoped>
.message-actions .p-button {
  width: 20px !important;
  height: 20px !important;
  padding: 0 !important;
  font-size: 0.6rem !important;
}

.message-actions .p-button .pi {
  font-size: 0.6rem !important;
}

.message-actions .p-button-xs {
  width: 18px !important;
  height: 18px !important;
}
</style>


