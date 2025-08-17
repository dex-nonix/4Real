<template>
  <div class="chat-widget surface-card p-3 border-round">
    <!-- Persona Selection Dialog -->
    <PersonaSelectionDialog
      v-model:visible="showPersonaDialog"
      @persona-selected="handlePersonaSelected"
    />

    <!-- History Management Dialog -->
    <HistoryManagementDialog
      v-if="currentSessionId"
      v-model:visible="showHistoryDialog"
      :session-id="currentSessionId"
      @history-selected="handleHistorySelected"
      @create-history="handleCreateHistory"
      @update-history="handleUpdateHistory"
      @delete-history="handleDeleteHistory"
    />

    <Chat
      :sessions="sessions"
      :current-session-id="currentSessionId"
      :current-history-id="currentHistoryId"
      :current-user-id="currentUserId"
      :messages="messages"
      @session-selected="handleSessionSelected"
      @history-selected="handleHistorySelected"
      @sendMessage="handleSendMessage"
      @closeChat="handleCloseChat"
      @viewHistory="showHistoryDialog = true"
      @renameHistory="handleRenameHistory"
      @addPersona="showPersonaDialog = true"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Chat from './components/Chat.vue'
import PersonaSelectionDialog from './components/PersonaSelectionDialog.vue'
import HistoryManagementDialog from './components/HistoryManagementDialog.vue'
import ChatRuntimeService from './services/ChatRuntimeService.js'
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

// Backend service
const chatService = new ChatRuntimeService()

// Toast for error notifications
const toast = useToast()

// State - FLAT DATA STRUCTURE (NO NESTED CRAP!)
const sessions = ref([])
const messages = ref([])
const currentSessionId = ref(null)
const currentHistoryId = ref(null)
const currentUserId = ref('user-self')
const loading = ref(false)

// UI State
const showPersonaDialog = ref(false)
const showHistoryDialog = ref(false)

// Computed values
const currentSession = computed(() => {
  if (!currentSessionId.value) return null
  return sessions.value.find(s => s.id === currentSessionId.value)
})

// Load flat data from CRUD endpoints (NO NESTED CRAP!)
const loadSessions = async () => {
  try {
    loading.value = true
    const response = await chatService.getSessions()
    // Handle CRUD response structure: {data: Array, pagination: {...}}
    sessions.value = response.data?.data || response.data || []
    
    if (sessions.value.length > 0 && !currentSessionId.value) {
      currentSessionId.value = sessions.value[0].id
    }
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Failed to Load Sessions',
      detail: error.message || 'Could not load sessions',
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

const loadMessages = async (historyId) => {
  try {
    const response = await chatService.getHistoryMessages(historyId)
    // Handle CRUD response structure: {data: Array, pagination: {...}}
    messages.value = response.data?.data || response.data || []
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Failed to Load Messages',
      detail: error.message || 'Could not load messages',
      life: 5000
    })
  }
}

// Event handlers
const handlePersonaSelected = async (persona) => {
  // PersonaSelectionDialog handles everything - just close it
  showPersonaDialog.value = false
  
  // CREATE NEW SESSION for this persona
  try {
    const sessionResponse = await chatService.createSession(persona.id, `Chat with ${persona.name}`)
    const newSession = sessionResponse.data
    
    // Set as current session
    currentSessionId.value = newSession.id
  } catch (error) {
    // Show error to user instead of swallowing it
    toast.add({
      severity: 'error',
      summary: 'Session Creation Failed',
      detail: error.message || 'Failed to create new session',
      life: 5000
    })
    return
  }
  
  // Reload sessions to get any new ones
  try {
    await loadSessions()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Session Reload Failed',
      detail: error.message || 'Failed to reload sessions',
      life: 5000
    })
  }
}

const handleSessionSelected = async (sessionId) => {
  currentSessionId.value = sessionId
}

const handleHistorySelected = async (historyId) => {
  currentHistoryId.value = historyId
  await loadMessages(historyId)
  
  // Close history dialog
  showHistoryDialog.value = false
  
  // Activate this history in the backend
  try {
    await chatService.updateSession(currentSessionId.value, {
      current_history_id: historyId
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Failed to Activate History',
      detail: error.message || 'Could not activate history',
      life: 5000
    })
  }
}

const handleCreateHistory = async (sessionId, title) => {
  try {
    const response = await chatService.createHistory(sessionId, title)
    const newHistory = response.data
    currentHistoryId.value = newHistory.id
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Failed to Create History',
      detail: error.message || 'Could not create history',
      life: 5000
    })
  }
}

const handleUpdateHistory = async (historyId, title, summary) => {
  try {
    await chatService.updateHistory(historyId, {
      title: title,
      summary: summary
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Failed to Update History',
      detail: error.message || 'Could not update history',
      life: 5000
    })
  }
}

const handleDeleteHistory = async (historyId) => {
  try {
    await chatService.deleteHistory(historyId)
    
    // If we deleted the current history, clear it
    if (currentHistoryId.value === historyId) {
      currentHistoryId.value = null
      messages.value = []
    }
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Failed to Delete History',
      detail: error.message || 'Could not delete history',
      life: 5000
    })
  }
}

const handleSendMessage = async (messageData) => {
  if (!currentHistoryId.value) return
  
  try {
    const response = await chatService.sendMessageToHistory(currentHistoryId.value, messageData)
    
    // Reload messages to get the new message
    await loadMessages(currentHistoryId.value)
    
    // Emit the message sent event
    emit('message-sent', response.data)
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Failed to Send Message',
      detail: error.message || 'Could not send message',
      life: 5000
    })
  }
}

const handleCloseChat = () => {
  // Handle chat close
  emit('closeChat')
}

const handleRenameHistory = async (historyId, newTitle) => {
  await handleUpdateHistory(historyId, newTitle)
}

// Initialize - ONLY SESSIONS!
onMounted(async () => {
  await loadSessions()
})
</script>

<style scoped>
.chat-widget {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
