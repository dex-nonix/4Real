<!-- ToolExecutionDialog.vue -->
<template>
  <Dialog 
    v-model:visible="dialogVisible" 
    :header="`Configure Tool: ${selectedTool?.name || 'Unknown Tool'}`" 
    modal 
    :style="{ width: '500px' }"
  >
    <div v-if="selectedTool" class="tool-form">
      <!-- Tool Description -->
      <div class="mb-3">
        <p class="text-600 mb-3">{{ selectedTool.description }}</p>
      </div>

      <!-- Dynamic Parameters Form -->
      <div v-if="selectedTool.parameters && selectedTool.parameters.length > 0" class="mb-3">
        <label class="block text-900 font-medium mb-2">Tool Parameters</label>
        
        <div class="space-y-3">
          <div v-for="param in selectedTool.parameters" :key="param.name" class="parameter-field">
            <label class="block text-700 text-sm mb-1">
              {{ param.name }}
              <span v-if="param.required" class="text-red-500">*</span>
              <span v-else class="text-500 text-xs">(optional)</span>
            </label>
            
            <!-- Input based on parameter type -->
            <InputText 
              v-if="param.type.includes('int')"
              v-model="toolFormData[param.name]" 
              :placeholder="`Enter ${param.name}${param.default ? ` (default: ${param.default})` : ''}`"
              class="w-full"
              type="number"
            />
            <InputText 
              v-else
              v-model="toolFormData[param.name]" 
              :placeholder="`Enter ${param.name}${param.default ? ` (default: ${param.default})` : ''}`"
              class="w-full"
              type="text"
            />
            
            <!-- Parameter info -->
            <div class="text-xs text-500 mt-1">
              Type: {{ param.type.replace('<class \'', '').replace('\'>', '') }}
              <span v-if="param.default !== null"> | Default: {{ param.default }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- No Parameters Message -->
      <div v-else class="text-center p-4">
        <i class="pi pi-check-circle text-2xl text-500 mb-2"></i>
        <p class="text-500">No parameters needed for this tool.</p>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-content-end gap-2">
        <Button 
          label="Cancel" 
          severity="secondary" 
          @click="closeDialog"
        />
        <Button 
          label="Execute Tool" 
          severity="primary" 
          @click="executeTool"
          :disabled="!selectedTool"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, defineExpose, defineEmits } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

// Props
const props = defineProps({
  selectedTool: { type: Object, required: false, default: null }
});

// Emits
const emit = defineEmits(['execute-tool']);

// Reactive state for dialog visibility
const dialogVisible = ref(false);
const toolFormData = ref({});

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

const executeTool = () => {
  emit('execute-tool', {
    tool: props.selectedTool.name,
    args: toolFormData.value
  });
  closeDialog();
};

// Expose functions to the parent component
defineExpose({
  openDialog,
  closeDialog
});
</script>

<style scoped>
.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mb-1 {
  margin-bottom: 0.25rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.block {
  display: block;
}

.w-full {
  width: 100%;
}
</style>
