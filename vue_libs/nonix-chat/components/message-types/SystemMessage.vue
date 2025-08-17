<!-- SystemMessage.vue -->
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

// Handle different field names from API
const messageContent = computed(() => props.message.content || props.message.content_json || props.message.text || 'System message');
const messageTimestamp = computed(() => props.message.timestamp || props.message.created_at || '');
</script>

<template>
  <div class="flex mb-4 justify-content-center">
    <div class="flex flex-column" style="max-width: 70%;">
      <div class="p-2 px-3 surface-100 border-round-xl text-center">
        <div class="flex align-items-center justify-content-center">
          <i class="pi pi-info-circle text-primary mr-2"></i>
          <span class="text-sm text-color-secondary">{{ messageContent }}</span>
        </div>
      </div>
      
      <div class="flex justify-content-center mt-1">
        <span class="text-xs text-color-secondary">{{ messageTimestamp }}</span>
      </div>
    </div>
  </div>
</template>
