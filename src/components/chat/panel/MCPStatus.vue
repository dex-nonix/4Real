<template>
  <div class="mcp-status">
    <div v-if="!servers || servers.length === 0" class="text-600">No MCP servers</div>
    <ul v-else class="m-0 p-0" style="list-style:none;">
      <li v-for="s in servers" :key="s.id" class="p-1 border-round surface-200 mb-1">
        <i class="pi pi-server mr-2" /> {{ s.name }}
        <span class="text-600 ml-2">{{ s.command }}</span>
        <span class="ml-2" :class="s.is_active ? 'text-green-600' : 'text-red-600'">{{ s.is_active ? 'active' : 'inactive' }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
defineProps({ servers: { type: Array, default: () => [] } })
</script>

<style scoped>
.mcp-status { width: 100%; }
</style>


