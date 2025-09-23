<template>
  <Card v-if="useCard && selectedFile" class="h-full">
    <template #title>
      <div class="flex justify-content-between align-items-center">
        <span class="text-lg font-medium">{{ selectedFile.title || selectedFile.original_filename }}</span>
        <Button
          icon="pi pi-times"
          size="small"
          text
          rounded
          @click="$emit('close')"
          v-tooltip="'Close Preview'"
          class="ml-2"
        />
      </div>
    </template>

    <NxFileView
      :selectedFile="selectedFile"
      :maximizeMode="'dialog'"
      @open-fullscreen-dialog="$emit('open-fullscreen-dialog')"
    />
  </Card>

  <div v-else-if="selectedFile" class="flex flex-column h-full surface-card border-round-lg">
    <div class="flex justify-content-between align-items-center p-3 border-bottom-1 surface-border bg-surface-section border-round-top-lg">
      <span class="text-lg font-medium">{{ selectedFile.title || selectedFile.original_filename }}</span>
      <Button
        icon="pi pi-times"
        size="small"
        text
        rounded
        @click="$emit('close')"
        v-tooltip="'Close Preview'"
        class="ml-2"
      />
    </div>

    <NxFileView
      :selectedFile="selectedFile"
      :maximizeMode="'dialog'"
      @open-fullscreen-dialog="$emit('open-fullscreen-dialog')"
    />
  </div>

  <div v-else class="no-selection">
    <div class="no-selection-content">
      <i class="pi pi-file" style="font-size: 3rem; color: var(--surface-border);"></i>
      <p>Select a file to preview</p>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import NxFileView from './NxFileView.vue'

// Props
const props = defineProps({
  selectedFile: {
    type: Object,
    default: null
  },
  useCard: { type: Boolean, default: false }
})

// Emits
const emit = defineEmits(['close', 'file-action', 'file-renamed', 'open-fullscreen-dialog'])
</script>

<style scoped>
.no-selection {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-selection-content {
  text-align: center;
  color: var(--text-color-secondary);
}

.no-selection-content p {
  margin: 1rem 0 0 0;
  font-size: 0.875rem;
}
</style>
