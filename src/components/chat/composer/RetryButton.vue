<template>
  <Button size="small" label="Retry" icon="pi pi-refresh" :disabled="disabled" @click="$emit('retry')" />
</template>

<script setup>
import Button from 'primevue/button'
defineProps({ disabled: { type: Boolean, default: false } })
defineEmits(['retry'])
</script>


