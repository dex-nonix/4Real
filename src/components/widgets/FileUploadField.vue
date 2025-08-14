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
      <i class="pi pi-check-circle text-green-500"></i>
      <span>{{ fileName }}</span>
    </div>
  </div>
  </template>

<script>
import FileUpload from 'primevue/fileupload'

export default {
  name: 'FileUploadField',
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
    return { fileName: '' }
  },
  methods: {
    onSelect(evt) {
      try {
        const file = (evt && evt.files && evt.files[0]) || null
        if (!file) return
        this.fileName = file.name
        // Emit the File object; the form submit handler/service will perform the upload
        this.$emit('update:modelValue', file)
      } catch (e) {
        this.$emit('error', e)
      }
    }
  }
}
</script>

<style scoped>
</style>


