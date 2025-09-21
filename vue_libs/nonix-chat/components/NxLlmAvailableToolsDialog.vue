<template>
  <Dialog
      :visible="visible"
      header="Persona Capabilities"
      modal
      :style="{ width: '90vw', maxWidth: '800px' }"
      class="p-dialog-sm"
      @update:visible="$emit('update:visible', $event)"
  >
    <div v-if="groupedTools.length > 0">
      <Accordion>
        <AccordionTab v-for="namespace in groupedTools" :key="namespace.namespace" :header="getNamespaceHeader(namespace)">
          <div class="space-y-2">
            <div v-for="tool in namespace.tools" :key="tool.name" class="flex items-center justify-between p-2 border rounded">
              <div class="flex-1">
                <div class="font-mono text-sm font-medium">{{ tool.name }}</div>
                <div class="text-xs text-600 mt-1">{{ tool.description }}</div>
              </div>
              <Button
                  icon="pi pi-play"
                  size="small"
                  @click="$emit('tool-selected', { ...tool, namespace: namespace.namespace, is_external: namespace.is_external })"
                  severity="primary"
                  class="p-button-sm ml-2"
                  text
                  rounded
              />
            </div>
          </div>
        </AccordionTab>
      </Accordion>
    </div>

    <div v-else class="text-center p-3">
      <i class="pi pi-info-circle text-2xl text-500"></i>
      <p class="text-500 text-sm mt-2">No tools available for this persona</p>
    </div>
  </Dialog>
</template>

<script setup>
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'

const props = defineProps({
  visible: Boolean,
  groupedTools: {
    type: Array,
    default: () => []
  },
  personaId: {
    type: [String, Number],
    default: null
  }
})

console.log('NxLlmAvailableToolsDialog props at init', { personaId: props.personaId, groupedTools: props.groupedTools?.length })

const emit = defineEmits(['update:visible', 'tool-selected'])

function getNamespaceHeader(namespace) {
  const icon = namespace.is_external ? '🔌' : '🏠'
  return `${icon} ${namespace.namespace} (${namespace.tools.length} tools)`
}
</script>

<style scoped>
/* Dialog-specific styles can be added here if needed */
</style>
