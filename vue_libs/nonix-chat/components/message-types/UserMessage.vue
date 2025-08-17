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
const messageTimestamp = computed(() => props.message.timestamp || props.message.created_at || '');
const messageSenderId = computed(() => props.message.senderId || props.message.role || '');
const isOwnMessage = computed(() => messageSenderId.value === props.currentUserId);
const userName = computed(() => props.message.metadata?.userName || `User ${messageSenderId.value}`);
const userAvatar = computed(() => props.message.metadata?.userAvatar || null);
const isValid = computed(() => props.message.metadata?.isValid !== false);
</script>

<template>
  <div class="flex mb-4" :class="isOwnMessage ? 'justify-content-end' : 'justify-content-start'">
    <div class="flex flex-column" style="max-width: 80%;">
      <!-- User Avatar/Identifier -->
      <div v-if="!isOwnMessage" class="flex align-items-center mb-1">
        <div v-if="userAvatar" class="w-2rem h-2rem border-circle overflow-hidden mr-2">
          <img :src="userAvatar" :alt="userName" class="w-full h-full object-cover" />
        </div>
        <div v-else class="w-2rem h-2rem border-circle bg-primary flex align-items-center justify-content-center mr-2">
          <span class="text-white text-sm font-bold">{{ userName.charAt(0).toUpperCase() }}</span>
        </div>
        <span class="text-xs text-color-secondary">{{ userName }}</span>
      </div>
      
      <!-- Message Content -->
      <div
          class="p-3 border-round-xl"
          :class="{
              'surface-primary text-primary-50': isOwnMessage,
              'surface-100 text-color': !isOwnMessage
          }"
      >
        <div class="flex align-items-start">
          <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">{{ messageContent }}</p>
          
          <!-- Validation Indicator -->
          <div v-if="!isOwnMessage" class="ml-2">
            <i v-if="isValid" class="pi pi-check-circle text-success text-sm"></i>
            <i v-else class="pi pi-exclamation-triangle text-warning text-sm"></i>
          </div>
        </div>
      </div>
      
      <!-- Timestamp and Status -->
      <div
        class="flex align-items-center mt-1 px-2"
        :class="{
          'justify-content-end': isOwnMessage,
          'justify-content-start': !isOwnMessage
        }"
      >
         <span class="text-xs text-color-secondary">{{ messageTimestamp }}</span>
         
         <!-- Input Validation Status -->
         <div v-if="!isOwnMessage && !isValid" class="ml-2">
           <span class="text-xs text-warning">Invalid input</span>
         </div>
      </div>
    </div>
  </div>
</template>
