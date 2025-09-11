<script setup>
const props = defineProps({
  toolName: {type: String, required: true},
  status: {type: String, required: true},
  toolRunId: {type: String, required: true}
});

const iconClass = (s) => {
  if (s === 'started') return 'pi pi-spin pi-spinner text-primary';
  if (s === 'completed' || s === 'success') return 'pi pi-check-circle text-success';
  if (s === 'error' || s === 'failed') return 'pi pi-times-circle text-danger';
  return 'pi pi-cog text-secondary';
};
</script>

<template>
  <span class="tool-run-badge inline-flex align-items-center gap-2 px-2 py-1 border-round surface-100">
    <i :class="iconClass(status)"/>
    <span class="font-medium">{{ toolName }}</span>
    <small class="text-color-secondary">{{ toolRunId }}</small>
  </span>
  <span class="mx-1"/>
</template>

<style scoped>
.tool-run-badge {
  border: 1px solid var(--surface-border);
}
</style>


