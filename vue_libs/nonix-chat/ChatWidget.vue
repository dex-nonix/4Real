<template>
  <div class="chat-widget surface-card p-3 border-round">
    <!-- Persona Selection Dialog -->
    <PersonaSelectionDialog
      v-model:visible="showPersonaDialog"
      :personas="personas"
      @persona-selected="handlePersonaSelected"
    />

    <!-- History Management Panel -->
    <Sidebar 
      v-model:visible="showHistoryPanel" 
      position="right" 
      :style="{ width: '400px' }"
    >
      <HistoryManagementPanel
        v-if="currentSession"
        :histories="currentSession.histories || []"
        :current-history-id="currentHistoryId"
        :session-id="currentSessionId"
        @history-selected="handleHistorySelected"
        @create-history="handleCreateHistory"
        @update-history="handleUpdateHistory"
        @delete-history="handleDeleteHistory"
      />
    </Sidebar>

    <Chat
      :personas="personas"
      :current-persona-id="currentPersonaId"
      :current-session-id="currentSessionId"
      :current-history-id="currentHistoryId"
      :current-user-id="currentUserId"
      @persona-selected="handlePersonaSelected"
      @session-selected="handleSessionSelected"
      @history-selected="handleHistorySelected"
      @sendMessage="handleSendMessage"
      @closeChat="handleCloseChat"
      @viewHistory="showHistoryPanel = true"
      @renameHistory="handleRenameHistory"
      @addPersona="showPersonaDialog = true"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Chat from './components/Chat.vue'
import PersonaSelectionDialog from './components/PersonaSelectionDialog.vue'
import HistoryManagementPanel from './components/HistoryManagementPanel.vue'
import Sidebar from 'primevue/sidebar'
import ChatRuntimeService from './services/ChatRuntimeService.js'

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

// Backend service
const chatService = new ChatRuntimeService()

// State
const personas = ref([])
const currentPersonaId = ref(null)
const currentSessionId = ref(null)
const currentHistoryId = ref(null)
const currentUserId = ref('user-self')
const loading = ref(false)

// UI State
const showPersonaDialog = ref(false)
const showHistoryPanel = ref(false)

// Computed values
const currentPersona = computed(() => {
  return personas.value.find(p => p.id === currentPersonaId.value)
})

const currentSession = computed(() => {
  return currentPersona.value?.sessions.find(s => s.id === currentSessionId.value)
})

const currentHistory = computed(() => {
  return currentSession.value?.histories.find(h => h.id === currentHistoryId.value)
})

// Load personas from backend
const loadPersonas = async () => {
  try {
    loading.value = true
    const response = await chatService.getPersonas()
    personas.value = response.data?.data || response.data || []
    
    if (personas.value.length > 0 && !currentPersonaId.value) {
      currentPersonaId.value = personas.value[0].id
      if (personas.value[0].sessions?.length > 0) {
        currentSessionId.value = personas.value[0].sessions[0].id
        if (personas.value[0].sessions[0].current_history_id) {
          currentHistoryId.value = personas.value[0].sessions[0].current_history_id
        }
      }
    }
  } catch (error) {
    console.error('Failed to load personas:', error)
  } finally {
    loading.value = false
  }
}

// Event handlers
const handlePersonaSelected = async (persona) => {
  currentPersonaId.value = persona.id
  
  // If persona has sessions, select the first one
  if (persona.sessions?.length > 0) {
    currentSessionId.value = persona.sessions[0].id
    if (persona.sessions[0].current_history_id) {
      currentHistoryId.value = persona.sessions[0].current_history_id
    } else if (persona.sessions[0].histories?.length > 0) {
      currentHistoryId.value = persona.sessions[0].histories[0].id
    }
  } else {
    // Create new session for this persona
    try {
      const response = await chatService.createSession(persona.id, `Chat with ${persona.name}`)
      const newSession = response.data?.data || response.data
      currentSessionId.value = newSession.id
      if (newSession.current_history_id) {
        currentHistoryId.value = newSession.current_history_id
      }
      // Reload personas to get updated session list
      await loadPersonas()
    } catch (error) {
      console.error('Failed to create session:', error)
    }
  }
}

const handleSessionSelected = async (sessionId) => {
  currentSessionId.value = sessionId
  const session = currentPersona.value?.sessions.find(s => s.id === sessionId)
  if (session?.current_history_id) {
    currentHistoryId.value = session.current_history_id
  } else if (session?.histories?.length > 0) {
    currentHistoryId.value = session.histories[0].id
  }
}

const handleHistorySelected = async (historyId) => {
  currentHistoryId.value = historyId
  // Activate this history in the backend
  try {
    await chatService.activateHistory(currentSessionId.value, historyId)
  } catch (error) {
    console.error('Failed to activate history:', error)
  }
}

const handleCreateHistory = async (sessionId, title) => {
  try {
    const response = await chatService.createHistory(sessionId, title)
    const newHistory = response.data?.data || response.data
    currentHistoryId.value = newHistory.id
    // Reload personas to get updated history list
    await loadPersonas()
  } catch (error) {
    console.error('Failed to create history:', error)
  }
}

const handleUpdateHistory = async (sessionId, historyId, title) => {
  try {
    await chatService.updateHistory(sessionId, historyId, title)
    // Reload personas to get updated data
    await loadPersonas()
  } catch (error) {
    console.error('Failed to update history:', error)
  }
}

const handleDeleteHistory = async (sessionId, historyId) => {
  try {
    await chatService.deleteHistory(sessionId, historyId)
    // Reload personas to get updated data
    await loadPersonas()
    
    // If we deleted the current history, select another one
    if (currentHistoryId.value === historyId) {
      const session = currentPersona.value?.sessions.find(s => s.id === sessionId)
      if (session?.histories?.length > 0) {
        currentHistoryId.value = session.histories[0].id
      } else {
        currentHistoryId.value = null
      }
    }
  } catch (error) {
    console.error('Failed to delete history:', error)
  }
}

const handleSendMessage = async ({ historyId, text }) => {
  try {
    // Send message to backend
    const response = await chatService.sendMessageToHistory(currentSessionId.value, historyId, text)
    
    // Reload personas to get updated message count
    await loadPersonas()
    
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

const handleRenameHistory = async (historyId, newTitle) => {
  try {
    await chatService.updateHistory(currentSessionId.value, historyId, newTitle)
    // Reload personas to get updated data
    await loadPersonas()
  } catch (error) {
    console.error('Failed to rename history:', error)
  }
}

const handleCloseChat = () => {
  console.log('Chat closed')
}

const handleAddPersona = () => {
  showPersonaDialog.value = true
}

// Initialize
onMounted(async () => {
  await loadPersonas()
  
  if (props.initialPersonaId) {
    currentPersonaId.value = props.initialPersonaId
  }
  
  if (props.initialSessionId) {
    currentSessionId.value = props.initialSessionId
  }
})
</script>

<style scoped>
.chat-widget { 
  width: 100%; 
  height: 100%;
}
</style>
