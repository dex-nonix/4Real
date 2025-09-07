<script setup>
import Badge from 'primevue/badge';
import Button from 'primevue/button';

const props = defineProps({
  turnId: { type: String, required: true },
  firstSeq: { type: Number, required: true },
  lastSeq: { type: Number, required: true },
  toolsCount: { type: Number, required: false, default: 0 },
  status: { type: String, required: false, default: 'in_progress' }
});
</script>

<template>
  <div class="turn-header flex align-items-center justify-content-between py-0 px-1 surface-100 border-round">
    <div class="flex align-items-center gap-1">
      <span class="text-xs text-color-secondary">Turn {{ firstSeq }}</span>
      <Button
        icon="pi pi-info-circle"
        text
        rounded
        size="small"
        severity="secondary"
        v-tooltip.bottom="`Turn ID: ${turnId}\nSequence: ${firstSeq} - ${lastSeq}\nStatus: ${status}\nTools: ${toolsCount}`"
      />
    </div>
    <div class="flex align-items-center gap-1">
      <Badge v-if="toolsCount > 0" :value="toolsCount" severity="info" size="small" />
    </div>
  </div>
</template>

<style scoped>
.turn-header {
  border-left: 2px solid var(--primary-color);
  font-size: 0.7rem;
  line-height: 1.1;
  min-height: 20px;
  margin-bottom: 0.25rem;
  opacity: 0.8;
}

.turn-header:hover {
  opacity: 1;
  transition: opacity 0.2s ease;
}
</style>


