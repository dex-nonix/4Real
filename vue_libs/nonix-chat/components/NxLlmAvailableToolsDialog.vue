<template>
  <Dialog
      :visible="visible"
      header="Available Tools"
      modal
      :style="{ width: '90vw', maxWidth: '700px' }"
      class="p-dialog-sm"
      @update:visible="$emit('update:visible', $event)"
  >
    <div v-if="tools.length > 0">
      <DataTable
          :value="tools"
          class="p-datatable-sm"
          :showGridlines="true"
          stripedRows
          responsiveLayout="scroll"
      >
        <Column field="name" header="Tool" style="width: 40%">
          <template #body="{ data }">
            <div class="font-mono text-sm">{{ data.name }}</div>
          </template>
        </Column>

        <Column field="description" header="Description" style="width: 45%">
          <template #body="{ data }">
            <div class="text-xs text-600">{{ data.description }}</div>
          </template>
        </Column>

        <Column header="Action" style="width: 15%">
          <template #body="{ data }">
            <Button
                icon="pi pi-play"
                size="small"
                @click="$emit('tool-selected', data)"
                severity="primary"
                class="p-button-sm"
                text
                rounded
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <div v-else class="text-center p-3">
      <i class="pi pi-info-circle text-2xl text-500"></i>
      <p class="text-500 text-sm mt-2">No tools available for this persona</p>
    </div>
  </Dialog>
</template>

<script setup>
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'

const props = defineProps({
  visible: Boolean,
  tools: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'tool-selected'])
</script>

<style scoped>
/* Dialog-specific styles can be added here if needed */
</style>
