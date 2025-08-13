<template>
  <div class="chat-tabs">
    <div class="flex align-items-center gap-2 flex-wrap">
      <div
        v-for="t in tabs"
        :key="t.id"
        class="p-1 px-2 border-round cursor-pointer"
        :class="t.id === activeTabId ? 'surface-300' : 'surface-100'"
        @click="$emit('activate-tab', t.id)"
      >
        <span>{{ t.title }}</span>
        <Button class="ml-2 p-button-text p-button-sm" icon="pi pi-times" @click.stop="$emit('close-tab', t.id)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'

defineProps({
  tabs: { type: Array, default: () => [] },
  activeTabId: { type: [String, null], default: null },
})

defineEmits(['activate-tab','close-tab'])
</script>

<style scoped>
.chat-tabs { width: 100%; }
</style>


