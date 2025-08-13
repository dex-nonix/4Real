<template>
  <div class="right-panel p-2 surface-100 border-round">
    <div class="flex align-items-center justify-content-between mb-2">
      <h4 class="m-0">Tools</h4>
      <Button size="small" icon="pi pi-refresh" @click="$emit('refresh-tools')" />
    </div>
    <ToolList :tools="tools" />

    <div class="flex align-items-center justify-content-between mt-4 mb-2">
      <h4 class="m-0">MCP</h4>
      <Button size="small" icon="pi pi-refresh" @click="$emit('refresh-mcp')" />
    </div>
    <MCPStatus :servers="mcpServers" />
  </div>
</template>

<script setup>
import Button from 'primevue/button'
import ToolList from '@/components/chat/panel/ToolList.vue'
import MCPStatus from '@/components/chat/panel/MCPStatus.vue'

defineProps({
  tools: { type: Array, default: () => [] },
  mcpServers: { type: Array, default: () => [] }
})

defineEmits(['refresh-tools','refresh-mcp'])
</script>

<style scoped>
.right-panel { width: 100%; }
</style>


