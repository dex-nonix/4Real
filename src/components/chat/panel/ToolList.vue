<template>
  <div class="tool-list">
    <div v-if="!tools || tools.length === 0" class="text-600">No tools available</div>
    <ul v-else class="m-0 p-0" style="list-style:none;">
      <li v-for="t in tools" :key="t" class="p-1 border-round surface-200 mb-1">
        <i class="pi pi-wrench mr-2" /> {{ t }}
      </li>
    </ul>
  </div>
</template>

<script setup>
defineProps({ tools: { type: Array, default: () => [] } })
</script>

<style scoped>
.tool-list { width: 100%; }
</style>


