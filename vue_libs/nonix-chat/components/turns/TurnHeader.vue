<script setup>
import Badge from 'primevue/badge';

const props = defineProps({
  turnId: { type: String, required: true },
  firstSeq: { type: Number, required: true },
  lastSeq: { type: Number, required: true },
  toolsCount: { type: Number, required: false, default: 0 },
  status: { type: String, required: false, default: 'in_progress' }
});
</script>

<template>
  <div class="turn-header flex align-items-center justify-content-between py-2 px-3 surface-100 border-round">
    <div class="flex align-items-center gap-2">
      <span class="font-medium">Turn</span>
      <span class="text-color-secondary">{{ turnId }}</span>
      <span class="ml-2">[{{ firstSeq }} - {{ lastSeq }}]</span>
    </div>
    <div class="flex align-items-center gap-2">
      <Badge v-if="toolsCount > 0" :value="toolsCount" severity="info" />
      <i :class="status === 'complete' ? 'pi pi-check-circle text-success' : status === 'error' ? 'pi pi-times-circle text-danger' : 'pi pi-spin pi-spinner text-primary'"/>
    </div>
  </div>
  <div class="mt-2" />
</template>

<style scoped>
.turn-header {
  border-left: 3px solid var(--primary-color);
}
</style>


