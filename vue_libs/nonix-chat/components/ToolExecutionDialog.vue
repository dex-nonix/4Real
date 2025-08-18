<!-- ToolExecutionDialog.vue -->
<template>
  <Dialog 
    v-model:visible="dialogVisible" 
    :header="`${selectedTool?.name || 'Tool'}`" 
    modal 
    :style="{ width: '90vw', maxWidth: '500px' }"
    class="p-dialog-sm"
  >
    <div v-if="selectedTool" class="tool-form">
      <!-- Tool Description -->
      <p class="text-600 mb-3 text-sm">{{ selectedTool.description }}</p>

      <!-- Dynamic Form for Parameters -->
      <DynamicForm
        v-if="selectedTool.parameters && selectedTool.parameters.length > 0"
        :config="formConfig"
        :initial-data="toolFormData"
        :submit-label="'Execute Tool'"
        @submit="handleFormSubmit"
        @cancel="closeDialog"
      />
      
      <!-- No Parameters -->
      <div v-else class="text-center p-3">
        <i class="pi pi-check-circle text-2xl text-500"></i>
        <p class="text-500 text-sm mt-2">No parameters needed</p>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, defineExpose, defineEmits, computed } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import DynamicForm from '@nonix/dynamic-form/DynamicForm.vue';

// Props
const props = defineProps({
  selectedTool: { type: Object, required: false, default: null }
});

// Emits
const emit = defineEmits(['execute-tool']);

// Reactive state for dialog visibility
const dialogVisible = ref(false);
const toolFormData = ref({});
const isSubmitting = ref(false);

// Dynamic form configuration computed from tool parameters
const formConfig = computed(() => {
  if (!props.selectedTool?.parameters) return { fields: [] };

  const config = {
    fields: props.selectedTool.parameters.map(param => ({
      key: param.name,                    // REQUIRED: unique identifier
      type: 'text',                       // REQUIRED: widget type
      label: param.name,                  // REQUIRED: display label
      required: param.required,           // OPTIONAL: validation
      props: {
        placeholder: param.name,
        class: 'w-full',
        ...(param.default !== null && { default: param.default })
      }
    }))
  };

  console.log('🔧 Form config generated:', config);
  console.log('🔧 Tool parameters:', props.selectedTool.parameters);

  return config;
});

// Functions to control the dialog
const openDialog = (toolData) => {
  // Initialize form data with default values from tool signature
  toolFormData.value = {};
  if (toolData && toolData.parameters) {
    for (const param of toolData.parameters) {
      if (param.default !== null) {
        toolFormData.value[param.name] = param.default;
      }
    }
  }
  dialogVisible.value = true;
};

const closeDialog = () => {
  dialogVisible.value = false;
  toolFormData.value = {};
};

const handleFormSubmit = async (formData) => {
  if (isSubmitting.value) return
  isSubmitting.value = true
  
  try {
    console.log('🔧 Form submitted with data:', formData);
    
    // Extract the actual form data from the submit event
    let args = {};
    
    if (formData && typeof formData === 'object') {
      // Use changedValues if available, otherwise fall back to __full
      if (formData.__full) {
        args = { ...formData.__full };
      } else if (Object.keys(formData).length > 0) {
        args = { ...formData };
      }
    }
    
    console.log('🔧 Final args to send:', args);
    
    emit('execute-tool', {
      tool: props.selectedTool.name,
      args: args
    });
    closeDialog();
  } catch (error) {
    console.error('Form submission error:', error);
  } finally {
    isSubmitting.value = false;
  }
};

// Expose functions to the parent component
defineExpose({
  openDialog,
  closeDialog
});
</script>

<style scoped>
:deep(.p-dialog) {
  margin: 1rem;
}

:deep(.p-datatable) {
  font-size: 0.875rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  padding: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem;
}

:deep(.p-inputtext-sm) {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>
