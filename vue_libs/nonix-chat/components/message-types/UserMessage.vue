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

// Handle different field names from API
const messageContent = computed(() => props.message.content || props.message.content_json || props.message.text || 'No content');
const userName = computed(() => props.message.metadata?.userName || `User ${props.message.senderId || props.message.role || ''}`);
const userAvatar = computed(() => props.message.metadata?.userAvatar || null);
const isValid = computed(() => props.message.metadata?.isValid !== false);
</script>

<template>
  <!-- User message content only - outer styling handled by MessageContainer -->
  
  <!-- User Avatar/Identifier -->
  <div v-if="props.message.senderId !== props.currentUserId && props.message.role !== props.currentUserId" class="flex align-items-center mb-2">
    <div v-if="userAvatar" class="w-2rem h-2rem border-circle overflow-hidden mr-2">
      <img :src="userAvatar" :alt="userName" class="w-full h-full object-cover" />
    </div>
    <div v-else class="w-2rem h-2rem border-circle bg-primary flex align-items-center justify-content-center mr-2">
      <span class="text-white text-sm font-bold">{{ userName.charAt(0).toUpperCase() }}</span>
    </div>
    <span class="text-xs text-500">{{ userName }}</span>
  </div>
  
  <!-- Message Content -->
  <div class="flex align-items-start">
    <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">{{ messageContent }}</p>
    
    <!-- Validation Indicator -->
    <div v-if="props.message.senderId !== props.currentUserId && props.message.role !== props.currentUserId" class="ml-2">
      <i v-if="isValid" class="pi pi-check-circle text-success text-sm"></i>
      <i v-else class="pi pi-exclamation-triangle text-warning text-sm"></i>
    </div>
  </div>
  
  <!-- Input Validation Status -->
  <div v-if="props.message.senderId !== props.currentUserId && props.message.role !== props.currentUserId && !isValid" class="mt-2">
    <span class="text-xs text-warning">Invalid input</span>
  </div>
</template>
