<template>
  <div class="flex align-items-center gap-1">
    <Button
      v-if="!showConfirm"
      :icon="icon"
      :size="size"
      :severity="severity"
      :disabled="disabled"
      text
      rounded
      @click.stop="showConfirm = true"
      v-tooltip.bottom="tooltip"
    />
    <div v-else class="flex align-items-center gap-1">
      <span class="text-sm text-red-500 mr-1">{{ confirmText }}</span>
      <Button
        :icon="confirmIcon"
        :size="size"
        :severity="confirmSeverity"
        text
        rounded
        class="tiny-button"
        @click.stop="onConfirm"
      />
      <Button
        :icon="cancelIcon"
        :size="size"
        :severity="cancelSeverity"
        text
        rounded
        class="tiny-button"
        @click.stop="onCancel"
      />
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'
import { ref } from 'vue'

const props = defineProps({
  icon: { type: String, required: true },
  confirmText: { type: String, default: 'Delete?' },
  confirmIcon: { type: String, default: 'pi pi-check' },
  cancelIcon: { type: String, default: 'pi pi-times' },
  severity: { type: String, default: 'danger' },
  confirmSeverity: { type: String, default: 'danger' },
  cancelSeverity: { type: String, default: 'secondary' },
  size: { type: String, default: 'small' },
  tooltip: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  showConfirmInitially: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'cancel'])

const showConfirm = ref(props.showConfirmInitially)

const onConfirm = () => {
  showConfirm.value = false
  emit('confirm')
}

const onCancel = () => {
  showConfirm.value = false
  emit('cancel')
}
</script>

<style scoped>
.tiny-button {
  width: 24px !important;
  height: 24px !important;
  min-width: 24px !important;
  padding: 0 !important;
}
</style>
