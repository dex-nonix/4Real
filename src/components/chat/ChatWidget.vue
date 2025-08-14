<template>
  <div class="chat-widget surface-card p-3 border-round">
    <ChatWorkspace
      :enable-left-panel="enableLeftPanel"
      :enable-right-panel="enableRightPanel"
      :personas="personas"
      :selected-persona-id="selectedPersonaId"
      :sessions="sessions"
      :open-tabs="openTabs"
      :active-tab-id="activeTabId"
      :messages-by-session="messagesBySession"
      :drafts-by-session="draftsBySession"
      :tools="effectiveTools"
      :mcp-servers="mcpServers"
      @send="handleSend"
      @retry="handleRetry"
      @update:selected-persona-id="(v) => { selectedPersonaId = v }"
      @open-session="(id) => openSession(id)"
      @new-session="handleNewSession"
      @activate-tab="(id) => activateTab(id)"
      @close-tab="handleCloseTab"
      @load-messages="(sid) => loadMessages(sid)"
      @update-draft="({ sessionId, text }) => setDraft(sessionId, text)"
      @refresh-tools="refreshTools"
      @refresh-mcp="refreshMcp"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Button from 'primevue/button'
import ChatWorkspace from '@/components/chat/ChatWorkspace.vue'
import useChatInstance from '@/hooks/useChatInstance.js'
import { useToast } from 'primevue/usetoast'

const props = defineProps({
  instanceId: { type: String, required: true },
  initialPersonaId: { type: Number, default: null },
  initialSessionId: { type: Number, default: null },
  persistKey: { type: String, default: null },
  enableLeftPanel: { type: Boolean, default: true },
  enableRightPanel: { type: Boolean, default: true },
  maxTabs: { type: Number, default: 8 },
  readonly: { type: Boolean, default: false },
  showMCPStatus: { type: Boolean, default: true }
})

defineEmits(['update:sessionId','tab-open','tab-close','message-sent','retry','error'])

const toast = useToast?.() || null

function handleErrorToast({ message, error }) {
  if (toast && toast.add) toast.add({ severity: 'error', summary: 'Chat Error', detail: message, life: 3000 })
}

const { 
  personas, sessions, openTabs, activeTabId, messagesBySession, draftsBySession,
  availableToolsByPersona, mcpServers,
  loadPersonas, loadSessions, openSession, createSession, loadMessages,
  sendMessage, retryLast, loadPersonaTools, loadMcpStatus, activateTab,
  setDraft,
} = useChatInstance({ instanceId: props.instanceId, persistKey: props.persistKey || `chat:${props.instanceId}`, onError: handleErrorToast })

let selectedPersonaId = ref(props.initialPersonaId)
const effectiveTools = ref([])

async function handleNewSession() {
  try {
    const personaId = selectedPersonaId.value || props.initialPersonaId || (personas.value[0]?.id ?? personas.value[0]?.value)
    if (!personaId) return
    await createSession({ personaId, title: 'New Chat' })
  } catch (e) {}
}

function handleCloseTab(tabId) {
  // reuse action via openTabs filter in hook
  const idx = openTabs.value.findIndex(t => t.id === tabId)
  if (idx >= 0) openTabs.value.splice(idx, 1)
  if (activeTabId.value === tabId) {
    activeTabId.value = openTabs.value.length ? openTabs.value[0].id : null
  }
}

async function handleSend(content) {
  const active = openTabs.value.find(t => t.id === activeTabId.value)
  if (!active?.sessionId) return
  await sendMessage(active.sessionId, content)
}

async function handleRetry() {
  const active = openTabs.value.find(t => t.id === activeTabId.value)
  if (!active?.sessionId) return
  await retryLast(active.sessionId)
}

async function refreshTools() {
  const personaId = selectedPersonaId.value || (personas.value[0]?.id ?? personas.value[0]?.value)
  if (!personaId) { effectiveTools.value = []; return }
  try {
    const res = await new (await import('@/app/services/ChatRuntimeService.js')).default().personaTools(personaId)
    effectiveTools.value = res.data?.data || res.data || []
  } catch { effectiveTools.value = [] }
}

async function refreshMcp() {
  try {
    const res = await new (await import('@/app/services/ChatRuntimeService.js')).default().mcpStatus()
    mcpServers.value = res.data?.data || res.data || []
  } catch {}
}

onMounted(async () => {
  await loadPersonas()
  await loadSessions()
  if (props.initialSessionId) {
    await openSession(props.initialSessionId)
  }
  await refreshTools()
  await refreshMcp()
})
</script>

<style scoped>
.chat-widget { width: 100%; }
</style>


