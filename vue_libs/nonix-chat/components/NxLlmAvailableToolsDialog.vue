<template>
  <Dialog
      :visible="visible"
      header="Persona Capabilities"
      modal
      :style="{ width: '90vw', maxWidth: '800px' }"
      class="p-dialog-sm"
      @update:visible="$emit('update:visible', $event)"
  >
    <TabView>
      <TabPanel header="Tools">
        <div v-if="tools.length > 0">
          <DataTable
              :value="tools"
              class="p-datatable-sm"
              :showGridlines="true"
              stripedRows
              responsiveLayout="scroll"
          >
            <Column field="name" header="Tool" style="width: 40%">
              <template #body="{ data }">
                <div class="font-mono text-sm">{{ data.name }}</div>
              </template>
            </Column>

            <Column field="description" header="Description" style="width: 45%">
              <template #body="{ data }">
                <div class="text-xs text-600">{{ data.description }}</div>
              </template>
            </Column>

            <Column header="Action" style="width: 15%">
              <template #body="{ data }">
                <Button
                    icon="pi pi-play"
                    size="small"
                    @click="$emit('tool-selected', data)"
                    severity="primary"
                    class="p-button-sm"
                    text
                    rounded
                />
              </template>
            </Column>
          </DataTable>
        </div>

        <div v-else class="text-center p-3">
          <i class="pi pi-info-circle text-2xl text-500"></i>
          <p class="text-500 text-sm mt-2">No tools available for this persona</p>
        </div>
      </TabPanel>

      <TabPanel header="MCP Servers">
        <div v-if="mcpServers.length > 0">
          <DataTable
              :value="mcpServers"
              class="p-datatable-sm"
              :showGridlines="true"
              stripedRows
              responsiveLayout="scroll"
          >
            <Column header="Funcs" style="width: 6%">
              <template #body="{ data }">
                <Button
                    icon="pi pi-list"
                    size="small"
                    class="p-button-plain"
                    :disabled="!data.is_active"
                    @click="openServerTools(data.persona_mcp_server_id)"
                    text
                />
              </template>
            </Column>
            <Column field="name" header="Server Name" style="width: 70%">
              <template #body="{ data }">
                <div class="font-mono text-sm">{{ data.name }}</div>
              </template>
            </Column>

            <Column field="is_active" header="Status" style="width: 30%">
              <template #body="{ data }">
                <Tag 
                    :value="data.is_active ? 'Active' : 'Inactive'"
                    :severity="data.is_active ? 'success' : 'danger'"
                    class="text-xs"
                />
              </template>
            </Column>
          </DataTable>
        </div>

        <div v-else class="text-center p-3">
          <i class="pi pi-info-circle text-2xl text-500"></i>
          <p class="text-500 text-sm mt-2">No MCP servers available for this persona</p>
        </div>
      </TabPanel>
    </TabView>

    <Dialog v-model:visible="showServerToolsDialog" header="Server Functions" modal :style="{ width: '80vw', maxWidth: '600px' }" class="p-dialog-sm">
      <div v-if="loadingServerTools" class="p-3 text-sm">Loading...</div>
      <div v-else>
        <DataTable :value="currentServerTools" class="p-datatable-sm">
          <Column field="name" header="Function" style="width: 40%">
            <template #body="{ data }"><div class="font-mono text-sm">{{ data.name }}</div></template>
          </Column>
          <Column field="description" header="Description" style="width: 45%">
            <template #body="{ data }"><div class="text-xs text-600">{{ data.description }}</div></template>
          </Column>
          <Column header="Action" style="width: 15%">
            <template #body="{ data }">
              <Button icon="pi pi-play" size="small" @click="onMcpToolSelected({ tool: data, persona_mcp_server_id: currentServer.id })" severity="primary" class="p-button-sm" text rounded/>
            </template>
          </Column>
        </DataTable>
      </div>
    </Dialog>
  </Dialog>
</template>

<script setup>
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Tag from 'primevue/tag'
import { ref } from 'vue'
import { inject } from 'vue'

const props = defineProps({
  visible: Boolean,
  tools: {
    type: Array,
    default: () => []
  },
  mcpServers: {
    type: Array,
    default: () => []
  },
  personaId: {
    type: [String, Number],
    default: null
  }
})

console.log('NxLlmAvailableToolsDialog props at init', { personaId: props.personaId, mcpServers: props.mcpServers && props.mcpServers.length })

const emit = defineEmits(['update:visible', 'tool-selected'])

const chatService = inject('chat-service')

// Server tools popup state
const showServerToolsDialog = ref(false)
const currentServer = ref(null)
const currentServerTools = ref([])
const serverToolsCache = ref({})
const loadingServerTools = ref(false)

async function openServerTools(personaMcpServerId) {
  console.log('openServerTools called for', personaMcpServerId)
  console.log('props.mcpServers length', props?.mcpServers?.length)
  if (!props || !props.mcpServers) {
    console.warn('No props or mcpServers available')
    return
  }
  const row = props.mcpServers.find(r => r.persona_mcp_server_id === personaMcpServerId)
  currentServer.value = row || { persona_mcp_server_id: personaMcpServerId }

  if (serverToolsCache.value[personaMcpServerId]) {
    currentServerTools.value = serverToolsCache.value[personaMcpServerId]
    showServerToolsDialog.value = true
    return
  }

  try {
    loadingServerTools.value = true
    const personaId = props.personaId || null
    console.log('personaId used:', personaId)
    if (!personaId) {
      console.error('personaId not provided to NxLlmAvailableToolsDialog')
      currentServerTools.value = []
      showServerToolsDialog.value = true
      return
    }

    let res
    try {
      res = await chatService.personaMcpServerTools(personaId)
    } catch (err) {
      console.error('chatService.personaMcpServerTools error', err)
      res = null
    }

    const map = {}
    if (Array.isArray(res)) {
      res.forEach(s => { map[s.persona_mcp_server_id] = s.tools || [] })
    } else if (res && res.data && Array.isArray(res.data)) {
      res.data.forEach(s => { map[s.persona_mcp_server_id] = s.tools || [] })
    } else {
      console.warn('Unexpected response from personaMcpServerTools', res)
    }
    serverToolsCache.value = map
    currentServerTools.value = map[personaMcpServerId] || []
    showServerToolsDialog.value = true
  } catch (e) {
    console.error('Failed to load server tools', e)
    currentServerTools.value = []
    showServerToolsDialog.value = true
  } finally {
    loadingServerTools.value = false
  }
}

function onMcpToolSelected(payload) {
  // bubble up to parent to open execution dialog
  emit('tool-selected', { ...payload, is_mcp: true })
  showServerToolsDialog.value = false
}
</script>

<style scoped>
/* Dialog-specific styles can be added here if needed */
</style>
