<template>
  <div class="persona-tools-viewer">
    <h3 class="mt-0">Available Tools</h3>
    <div v-if="loading" class="text-sm text-gray-600">Loading tools...</div>
    <ul v-else class="list-none p-0 m-0 flex flex-column gap-2">
      <li v-for="tool in tools" :key="tool" class="tool-item p-3 surface-100 border-round">
        <div class="flex align-items-center gap-3">
          <i class="pi pi-wrench text-primary"></i>
          <div class="flex-1">
            <span class="font-mono text-sm">{{ tool }}</span>
          </div>
          <Button 
            icon="pi pi-play" 
            size="small" 
            @click="executeTool(tool)"
            :label="'Execute'"
            severity="primary"
          />
        </div>
      </li>
      <li v-if="!tools.length" class="text-sm text-gray-600 p-3 surface-100 border-round">
        No tools available for this persona
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, inject } from 'vue'
import Button from 'primevue/button'

export default {
  name: 'PersonaToolsViewer',
  components: {
    Button
  },
  props: {
    personaId: { type: [String, Number], required: true }
  },
  setup(props, { emit }) {
    const tools = ref([])
    const loading = ref(false)
    
    // Inject the chat service that's already available
    const chatService = inject('chat-service')

    const load = async () => {
      loading.value = true
      try {
        if (chatService) {
          // Use the existing ChatService method
          const toolsData = await chatService.personaTools(props.personaId)
          tools.value = Array.isArray(toolsData) ? toolsData : []
        } else {
          // Fallback to direct API call if service not available
          const { API_BASE_URL } = await import('@/env.js')
          const res = await fetch(`${API_BASE_URL}/chat/personas/${props.personaId}/tools`)
          const data = await res.json()
          tools.value = Array.isArray(data?.data) ? data.data : []
        }
      } catch (e) {
        console.error('Failed to load tools:', e)
        tools.value = []
      } finally {
        loading.value = false
      }
    }

    const executeTool = async (toolName) => {
      try {
        // Emit tool execution event for parent components to handle
        // This integrates with the existing chat flow
        emit('tool-executed', {
          tool: toolName,
          persona_id: props.personaId,
          args: {} // Default empty args, can be enhanced later
        })
        
        console.log('Tool execution initiated:', toolName)
      } catch (error) {
        console.error('Tool execution failed:', error)
      }
    }

    return {
      tools,
      loading,
      load,
      executeTool
    }
  },
  mounted() { this.load() },
  watch: {
    personaId() { this.load() }
  }
}
</script>

<style scoped>
.tool-item {
  transition: all 0.2s ease;
}

.tool-item:hover {
  background-color: var(--surface-200) !important;
  transform: translateX(2px);
}

.tool-item .pi-wrench {
  font-size: 1.2rem;
}
</style>


