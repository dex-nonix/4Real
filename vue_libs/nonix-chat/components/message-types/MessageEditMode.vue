<template>
  <div class="edit-mode-compact">
    <div class="edit-actions-overlay">
      <Button
        icon="pi pi-times"
        text
        severity="secondary"
        size="small"
        @click="handleCancel"
        class="edit-action-btn"
        v-tooltip="'Cancel (Esc)'"
      />
      <Button
        icon="pi pi-check"
        text
        severity="success"
        size="small"
        @click="handleSave"
        class="edit-action-btn"
        v-tooltip="'Save (Enter)'"
      />
    </div>

    <Textarea
      :model-value="modelValue"
      class="edit-textarea-compact"
      :autoResize="true"
      rows="1"
      :placeholder="placeholder"
      @update:model-value="$emit('update:modelValue', $event)"
      @keydown="handleKeyDown"
    />
  </div>
</template>

<script setup>
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Edit message...'
  },
  messageId: {
    type: [String, Number],
    required: true
  },
  originalContent: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:modelValue', 'save', 'cancel', 'keydown', 'edit', 'cancel-edit']);

const handleSave = () => {
  if (props.modelValue.trim() !== props.originalContent) {
    emit('edit', {
      messageId: props.messageId,
      newContent: props.modelValue.trim(),
      originalContent: props.originalContent
    });
  }
  emit('cancel-edit');
};

const handleCancel = () => {
  emit('update:modelValue', props.originalContent);
  emit('cancel-edit');
};

const handleKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    handleSave();
  } else if (event.key === 'Escape') {
    event.preventDefault();
    handleCancel();
  }
  emit('keydown', event);
};
</script>

<style scoped>
.edit-mode-compact {
  position: relative;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  min-height: 2rem;
  display: block !important;
}

.edit-actions-overlay {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 10;
  display: flex;
  gap: 0.25rem;
  background: var(--surface-section);
  border-radius: 4px;
  padding: 0.125rem;
}

.edit-action-btn {
  width: 20px !important;
  height: 20px !important;
  padding: 2px !important;
  background: transparent !important;
  border: none !important;
  border-radius: 3px !important;
}

.edit-action-btn:hover {
  background: var(--surface-hover) !important;
}

.edit-action-btn.p-button-success {
  color: var(--green-500) !important;
}

.edit-action-btn.p-button-success:hover {
  background: rgba(25, 135, 84, 0.1) !important;
  color: var(--green-600) !important;
}

.edit-textarea-compact {
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  font-family: inherit !important;
  font-size: 0.875rem !important;
  line-height: 1.4 !important;
  border: none !important;
  background: transparent !important;
  color: var(--text-color) !important;
  padding: 0 !important;
  margin: 0 !important;
  resize: vertical !important;
  outline: none !important;
  box-shadow: none !important;
  min-height: 1.4rem !important;
  display: block !important;
}

.edit-textarea-compact:focus {
  outline: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

.edit-textarea-compact::placeholder {
  color: var(--text-color-secondary) !important;
}
</style>
