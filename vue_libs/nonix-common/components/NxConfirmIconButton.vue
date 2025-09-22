<template>
  <div class="flex align-items-center gap-1">
    <Button
      v-if="!showConfirm"
      :icon="icon"
      :size="triggerSize"
      :severity="severity"
      :disabled="disabled"
      :class="{ 'tiny-button': isTiny }"
      text
      rounded
      @click.stop="openConfirm"
      v-tooltip.bottom="tooltip"
    />
    <div v-else class="flex align-items-center gap-1">
      <span class="text-sm text-red-500 mr-1">{{ confirmText }}</span>
      <Button
        :icon="confirmIcon"
        :size="triggerSize"
        :severity="confirmSeverity"
        :class="{ 'tiny-button': isTiny }"
        text
        rounded
        @click.stop="onConfirm"
      />
      <Button
        :icon="cancelIcon"
        :size="triggerSize"
        :severity="cancelSeverity"
        :class="{ 'tiny-button': isTiny }"
        text
        rounded
        @click.stop="onCancel"
      />
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'
import { ref, computed } from 'vue'

const props = defineProps({
  icon: { type: String, required: true },
  confirmText: { type: String, default: 'Delete?' },
  confirmIcon: { type: String, default: 'pi pi-check' },
  cancelIcon: { type: String, default: 'pi pi-times' },
  severity: { type: String, default: 'danger' },
  confirmSeverity: { type: String, default: 'danger' },
  cancelSeverity: { type: String, default: 'secondary' },
  size: { type: String, default: null }, // 'normal' (default), 'small', 'tiny'
  tooltip: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  showConfirmInitially: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'cancel', 'state-change'])

const showConfirm = ref(props.showConfirmInitially)

const isTiny = computed(() => props.size === 'tiny')
const triggerSize = computed(() => (props.size === 'small' || props.size === 'tiny') ? 'small' : null)

const openConfirm = () => {
  showConfirm.value = true
  emit('state-change', true)
}

const onConfirm = () => {
  showConfirm.value = false
  emit('state-change', false)
  emit('confirm')
}

const onCancel = () => {
  showConfirm.value = false
  emit('state-change', false)
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
