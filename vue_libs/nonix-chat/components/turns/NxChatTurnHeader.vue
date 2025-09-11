<script setup>
import Badge from 'primevue/badge';
import Button from 'primevue/button';

const props = defineProps({
  turnId: {type: String, required: true},
  firstSeq: {type: Number, required: true},
  lastSeq: {type: Number, required: true},
  toolsCount: {type: Number, required: false, default: 0},
  status: {type: String, required: false, default: 'in_progress'}
});
</script>

<template>
  <div class="turn-header flex align-items-center justify-content-between py-0 px-0">
    <span class="text-xs text-color-secondary">Turn {{ firstSeq }}</span>
    <div class="flex align-items-center gap-0">
      <Badge v-if="toolsCount > 0" :value="toolsCount" severity="info" size="small"/>
      <Button
          icon="pi pi-info-circle"
          text
          rounded
          size="small"
          severity="secondary"
          class="info-btn"
          v-tooltip.bottom="`Turn ID: ${turnId}\nSequence: ${firstSeq} - ${lastSeq}\nStatus: ${status}\nTools: ${toolsCount}`"
      />
    </div>
  </div>
</template>

<style scoped>
.turn-header {
  font-size: 0.65rem;
  line-height: 1;
  min-height: 16px;
  margin-bottom: 0.125rem;
  opacity: 0.7;
  padding: 0.125rem 0;
}

.turn-header:hover {
  opacity: 1;
  transition: opacity 0.2s ease;
}

.info-btn {
  font-size: 0.6rem !important;
  width: 16px !important;
  height: 16px !important;
  padding: 0 !important;
}

.info-btn .pi {
  font-size: 0.5rem !important;
}
</style>


