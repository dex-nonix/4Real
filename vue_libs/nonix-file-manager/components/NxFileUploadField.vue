<template>
  <div class="flex flex-column gap-2">
    <FileUpload
      mode="basic"
      name="file"
      :choose-label="buttonLabel"
      :auto="false"
      :custom-upload="false"
      @select="onSelect"
    />
    <small v-if="hint" class="text-500">{{ hint }}</small>
    <div v-if="fileName" class="flex align-items-center gap-2">
      <i class="pi pi-file"></i>
      <span class="font-medium">{{ fileName }}</span>
    </div>
  </div>
  </template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import FileUpload from 'primevue/fileupload'

// Props
const props = defineProps({
  modelValue: { type: [Number, String, Object], default: null },
  title: { type: String, default: '' },
  categoryId: { type: [Number, String], default: null },
  buttonLabel: { type: String, default: 'Choose File' },
  hint: { type: String, default: '' }
})

// Emits
const emit = defineEmits(['update:modelValue', 'uploaded', 'error'])

// Reactive state
const fileName = ref('')
const progressKey = ref(`up_${Math.random().toString(36).slice(2)}`)
const progress = ref(0)

// Methods
const onSelect = (evt) => {
  try {
    const file = (evt && evt.files && evt.files[0]) || null
    if (!file) return
    fileName.value = file.name
    // Emit wrapper with file + progressKey so service can stream progress events
    emit('update:modelValue', { file, progressKey: progressKey.value })
    // Listen for progress events
    const onProg = (e) => {
      if (e && e.detail && e.detail.key === progressKey.value) progress.value = e.detail.progress || 0
    }
    const onDone = (e) => {
      if (e && e.detail && e.detail.key === progressKey.value) {
        progress.value = 100
        window.removeEventListener('upload:progress', onProg)
        window.removeEventListener('upload:done', onDone)
      }
    }
    window.addEventListener('upload:progress', onProg)
    window.addEventListener('upload:done', onDone)
  } catch (e) {
    emit('error', e)
  }
}
</script>

<style scoped>
</style>


