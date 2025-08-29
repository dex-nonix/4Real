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
    <div class="flex align-items-center justify-content-between">
      <div class="text-xs text-400">{{ message.created_at }}</div>
      <div class="flex align-items-center gap-1">
        <button v-if="isStreamable && isStreaming" class="p-button p-button-text p-button-rounded p-button-danger p-button-sm" @click="$emit('stop', message.id)">
          <i class="pi pi-stop"></i>
        </button>
        <button v-if="canCopy" class="p-button p-button-text p-button-rounded p-button-sm" @click="$emit('copy', message.id)">
          <i class="pi pi-copy"></i>
        </button>
        <button v-if="canDelete" class="p-button p-button-text p-button-rounded p-button-sm" @click="$emit('delete', message.id)">
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
</style>


