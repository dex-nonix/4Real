<!-- UserMessage.vue -->
<script setup>
import { computed } from 'vue';

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: [String, Number],
    required: true
  }
});

const emit = defineEmits(['deleteMessage']);

// Single canonical source: message.content_json.text
const messageContent = computed(() => props.message?.content_json?.text || '');
const userName = computed(() => props.message.metadata?.userName || '');
const userAvatar = computed(() => props.message.metadata?.userAvatar || null);
const isValid = computed(() => props.message.metadata?.isValid !== false);
</script>

<template>
  <!-- User message content only - outer styling handled by MessageContainer -->
  
  <!-- No header/avatar for user messages -->
  
  <!-- Message Content -->
  <div class="flex align-items-start justify-content-end">
    <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">{{ messageContent }}</p>
    
    <!-- Validation Indicator -->
    <div v-if="props.message.senderId !== props.currentUserId && props.message.role !== props.currentUserId" class="ml-2">
      <i v-if="isValid" class="pi pi-check-circle text-success text-sm"></i>
      <i v-else class="pi pi-exclamation-triangle text-warning text-sm"></i>
    </div>
  </div>
  
  <!-- Input Validation Status -->
  <div v-if="!isValid" class="mt-2">
    <span class="text-xs text-warning">Invalid input</span>
  </div>
</template>
