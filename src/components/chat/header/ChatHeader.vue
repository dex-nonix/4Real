<template>
  <div class="flex align-items-center justify-content-between mb-3">
    <div class="flex align-items-center gap-2">
      <i class="pi pi-comments" />
      <strong>{{ title }}</strong>
      <span v-if="personaName" class="text-500">— {{ personaName }}</span>
    </div>
    <div class="flex align-items-center gap-2">
      <Button size="small" label="New Session" icon="pi pi-plus" @click="$emit('new-session')" />
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'

defineProps({
  title: { type: String, default: 'Chat' },
  personaName: { type: String, default: '' },
})

defineEmits(['new-session'])
</script>


