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

<script>
import FileUpload from 'primevue/fileupload'

export default {
  name: 'NxFileUploadField',
  components: { FileUpload },
  props: {
    modelValue: { type: [Number, String, Object], default: null },
    title: { type: String, default: '' },
    categoryId: { type: [Number, String], default: null },
    buttonLabel: { type: String, default: 'Choose File' },
    hint: { type: String, default: '' }
  },
  emits: ['update:modelValue', 'uploaded', 'error'],
  data() {
    return { fileName: '', progressKey: `up_${Math.random().toString(36).slice(2)}`, progress: 0 }
  },
  methods: {
    onSelect(evt) {
      try {
        const file = (evt && evt.files && evt.files[0]) || null
        if (!file) return
        this.fileName = file.name
        // Emit wrapper with file + progressKey so service can stream progress events
        this.$emit('update:modelValue', { file, progressKey: this.progressKey })
        // Listen for progress events
        const onProg = (e) => {
          if (e && e.detail && e.detail.key === this.progressKey) this.progress = e.detail.progress || 0
        }
        const onDone = (e) => {
          if (e && e.detail && e.detail.key === this.progressKey) {
            this.progress = 100
            window.removeEventListener('upload:progress', onProg)
            window.removeEventListener('upload:done', onDone)
          }
        }
        window.addEventListener('upload:progress', onProg)
        window.addEventListener('upload:done', onDone)
      } catch (e) {
        this.$emit('error', e)
      }
    }
  }
}
</script>

<style scoped>
</style>


