<template>
  <Dialog
    v-model:visible="visible"
    modal
    :header="selectedFile?.title || selectedFile?.original_filename || 'File View'"
    :style="dialogStyle"
  >
    <!-- NxFileView with fullscreen maximizeMode -->
    <div v-if="selectedFile">
      <NxFileView :selectedFile="selectedFile" :maximizeMode="'fullscreen'" />
    </div>
    <div v-else>
      <p>No file selected</p>
    </div>

    <template #footer>
      <Button
        :label="isFullscreen ? 'Minimize' : 'Maximize'"
        :icon="isFullscreen ? 'pi pi-minus' : 'pi pi-expand'"
        @click="toggleFullscreen"
      />
      <Button
        label="Close"
        icon="pi pi-times"
        class="p-button-text"
        @click="visible = false"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import NxFileView from './NxFileView.vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  selectedFile: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:visible'])

// Reactive state
const isFullscreen = ref(false)

// Computed properties
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dialogStyle = computed(() => {
  if (isFullscreen.value) {
    return {
      width: '100vw',
      height: '100vh',
      maxWidth: 'none',
      margin: 0,
      top: 0,
      left: 0
    }
  }
  return { width: '80vw', height: '80vh', maxWidth: '1200px' }
})

// Methods
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}
</script>

<style scoped>
/* No custom styles needed - using PrimeVue Dialog styling */
</style>

