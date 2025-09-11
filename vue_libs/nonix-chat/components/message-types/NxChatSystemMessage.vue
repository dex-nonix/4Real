<script setup>
import {computed} from 'vue';

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
</script>

<template>
  <!-- System message content only - outer styling handled by MessageContainer -->
  <div class="text-center">
    <span class="text-sm">{{ messageContent }}</span>
  </div>
</template>
