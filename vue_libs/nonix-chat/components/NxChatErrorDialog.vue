<template>
  <Dialog v-model:visible="dialogVisible" modal header="Error Log" :style="{ width: '80vw', maxWidth: '800px' }">
    <div class="flex flex-column gap-3">
      <!-- Action Bar -->
      <div class="flex justify-content-between align-items-center">
        <div class="flex align-items-center gap-2">
          <span class="text-sm text-500">{{ errors.length }} error(s)</span>
        </div>
        <div class="flex gap-2">
          <Button 
            label="Copy Selected" 
            icon="pi pi-copy" 
            size="small" 
            :disabled="selectedErrors.length === 0"
            @click="copySelected"
          />
          <Button 
            label="Clear All" 
            icon="pi pi-trash" 
            size="small" 
            severity="danger" 
            :disabled="errors.length === 0"
            @click="clearAll"
          />
        </div>
      </div>

      <!-- Error Table -->
      <DataTable 
        :value="errors" 
        v-model:selection="selectedErrors"
        selectionMode="multiple"
        dataKey="id"
        :paginator="true"
        :rows="10"
        :rowsPerPageOptions="[5, 10, 20]"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} errors"
        responsiveLayout="scroll"
        class="p-datatable-sm"
      >
        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
        
        <Column field="message" header="Error Message" sortable>
          <template #body="{ data }">
            <div class="font-semibold text-red-600">{{ data.message }}</div>
          </template>
        </Column>
        
        <Column field="timestamp" header="Time" sortable style="width: 150px">
          <template #body="{ data }">
            <span class="text-sm text-500">{{ formatTime(data.timestamp) }}</span>
          </template>
        </Column>
        
        <Column field="details" header="Details" style="width: 200px">
          <template #body="{ data }">
            <div v-if="data.details" class="text-xs text-600">
              {{ truncateDetails(data.details) }}
            </div>
            <span v-else class="text-xs text-400">No details</span>
          </template>
        </Column>
        
        <Column header="Actions" style="width: 120px">
          <template #body="{ data }">
            <div class="flex gap-1">
              <Button 
                icon="pi pi-copy" 
                size="small" 
                text 
                rounded
                @click="copyError(data)"
                v-tooltip.left="'Copy Error'"
              />
              <Button 
                icon="pi pi-times" 
                size="small" 
                text 
                rounded
                severity="danger"
                @click="deleteError(data.id)"
                v-tooltip.left="'Delete Error'"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <template #footer>
      <Button label="Close" icon="pi pi-times" @click="closeDialog" class="p-button-text" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, defineExpose } from 'vue';
import Dialog from 'primevue/dialog';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';

// Props
const props = defineProps({
  errors: { type: Array, required: true }
});

// Reactive state for dialog visibility
const dialogVisible = ref(false);
const selectedErrors = ref([]);

// Functions to control the dialog
const openDialog = () => {
  dialogVisible.value = true;
};

const closeDialog = () => {
  dialogVisible.value = false;
};

// Expose functions to the parent component
defineExpose({
  openDialog,
  closeDialog
});

const formatTime = (timestamp) => {
  if (!timestamp) return 'Unknown';
  try {
    return new Date(timestamp).toLocaleString();
  } catch {
    return 'Invalid time';
  }
};

const truncateDetails = (details) => {
  if (!details) return '';
  const text = typeof details === 'object' ? JSON.stringify(details) : String(details);
  return text.length > 50 ? text.substring(0, 50) + '...' : text;
};

const copyError = (error) => {
  const errorText = `Error: ${error.message}\nTime: ${formatTime(error.timestamp)}\nDetails: ${error.details || 'No details'}`;
  navigator.clipboard.writeText(errorText);
};

const copySelected = () => {
  if (selectedErrors.value.length === 0) return;
  
  const errorTexts = selectedErrors.value.map(error => 
    `Error: ${error.message}\nTime: ${formatTime(error.timestamp)}\nDetails: ${error.details || 'No details'}`
  ).join('\n\n');
  
  navigator.clipboard.writeText(errorTexts);
};

const deleteError = (errorId) => {
  // This will be handled by parent via ref
};

const clearAll = () => {
  // This will be handled by parent via ref
};
</script>

<style scoped>
:deep(.p-datatable) {
  font-size: 0.875rem;
}

:deep(.p-datatable .p-datatable-header) {
  background: var(--surface-50);
  border: 1px solid var(--surface-200);
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: var(--surface-100);
  border: 1px solid var(--surface-200);
  font-weight: 600;
  font-size: 0.875rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  border: 1px solid var(--surface-200);
  padding: 0.5rem;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background: var(--surface-50);
}
</style>
