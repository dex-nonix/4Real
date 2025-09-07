<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: { type: Object, required: true },
  isStreamable: { type: Boolean, default: true },
  canDelete: { type: Boolean, default: true },
  canCopy: { type: Boolean, default: true }
})

const emit = defineEmits(['delete', 'copy', 'stop'])

const isStreaming = computed(() => props.message?.status === 'streaming' || props.message?.status === 'processing')
</script>

<template>
  <div class="flex flex-column gap-1">
    <div class="flex align-items-center justify-content-end">
      <div class="flex align-items-center gap-0 message-actions">
        <button v-if="isStreamable && isStreaming" class="p-button p-button-text p-button-rounded p-button-danger p-button-xs" @click="$emit('stop', message.id)">
          <i class="pi pi-stop"></i>
        </button>
        <button v-if="canCopy" class="p-button p-button-text p-button-rounded p-button-xs" @click="$emit('copy', message.id)">
          <i class="pi pi-copy"></i>
        </button>
        <button v-if="canDelete" class="p-button p-button-text p-button-rounded p-button-xs" @click="$emit('delete', message.id)">
          <i class="pi pi-trash"></i>
        </button>
      </div>
    </div>
    <div>
      <slot></slot>
    </div>
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


