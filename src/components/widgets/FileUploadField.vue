<template>
  <div class="flex flex-column gap-2">
    <FileUpload
      mode="basic"
      name="file"
      :choose-label="buttonLabel"
      :custom-upload="true"
      @uploader="onUpload"
    />
    <small v-if="hint" class="text-500">{{ hint }}</small>
    <div v-if="uploaded" class="flex align-items-center gap-2">
      <i class="pi pi-check-circle text-green-500"></i>
      <span>{{ uploaded.original_filename }}</span>
    </div>
  </div>
  </template>

<script>
import FileUpload from 'primevue/fileupload'
import { inject } from 'vue'

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
    return { uploaded: null }
  },
  setup() {
    const filesService = inject('files')
    return { filesService }
  },
  methods: {
    async onUpload(evt) {
      try {
        const file = (evt && evt.files && evt.files[0]) || null
        if (!file) return
        const res = await this.filesService.upload(file, { title: this.title, category_id: this.categoryId })
        const created = res?.data?.data || res?.data
        this.uploaded = created
        this.$emit('uploaded', created)
        // Emit id or full object depending on consumer expectation
        this.$emit('update:modelValue', created?.id ?? created)
      } catch (e) {
        this.$emit('error', e)
      }
    }
  }
}
</script>

<style scoped>
</style>


