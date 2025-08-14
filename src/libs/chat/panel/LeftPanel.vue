<template>
  <div class="left-panel p-2 surface-100 border-round">
    <h4 class="m-0 mb-2">Left Panel</h4>
    <div class="mb-3">
      <label class="block text-600 mb-1">Persona</label>
      <Dropdown class="w-full" :options="personaOptions" optionLabel="label" optionValue="value" v-model="localPersona" @change="emitPersona" />
    </div>
    <div>
      <div class="flex align-items-center justify-content-between mb-2">
        <label class="block text-600">Sessions</label>
        <Button size="small" label="New" icon="pi pi-plus" @click="$emit('new-session')" />
      </div>
      <div class="flex flex-column gap-2" style="max-height: 220px; overflow:auto;">
        <Button v-for="s in sessions" :key="s.id" class="p-button-sm p-button-text justify-content-start" :label="s.title || ('Session ' + s.id)" icon="pi pi-angle-right" @click="$emit('open-session', s.id)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'

const props = defineProps({
  personas: { type: Array, default: () => [] },
  selectedPersonaId: { type: [Number, String], default: null },
  sessions: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:selected-persona-id','open-session','new-session'])

const localPersona = ref(props.selectedPersonaId)
watch(() => props.selectedPersonaId, v => { localPersona.value = v })

const personaOptions = computed(() => props.personas.map(p => ({ label: p.label || p.name, value: p.value ?? p.id })))

function emitPersona() {
  emit('update:selected-persona-id', localPersona.value)
}
</script>

<style scoped>
.left-panel { width: 100%; }
</style>


