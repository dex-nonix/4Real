<!-- SystemMessage.vue -->
<script setup>
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
</script>

<template>
  <div class="flex mb-4 justify-content-center">
    <div class="flex flex-column" style="max-width: 70%;">
      <div class="p-2 px-3 surface-100 border-round-xl text-center">
        <div class="flex align-items-center justify-content-center">
          <i class="pi pi-info-circle text-primary mr-2"></i>
          <span class="text-sm text-color-secondary">{{ message.text }}</span>
        </div>
      </div>
      
      <div class="flex justify-content-center mt-1">
        <span class="text-xs text-color-secondary">{{ message.timestamp }}</span>
      </div>
    </div>
  </div>
</template>
