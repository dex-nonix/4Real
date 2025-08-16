<template>
  <div class="chat-widget surface-card p-3 border-round">
    <Chat
      :sessions="sessions"
      :messages="activeMessages"
      :current-user-id="currentUserId"
      @session-selected="handleSessionSelected"
      @sendMessage="handleSendMessage"
      @closeChat="handleCloseChat"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Chat from './components/Chat.vue'
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
const sessions = ref([])
const messagesBySession = ref({})
const currentUserId = ref('user-self')
const selectedSessionId = ref(null)
const loading = ref(false)

// Computed for active messages
const activeMessages = computed(() => {
  if (!selectedSessionId.value) return []
  return messagesBySession.value[selectedSessionId.value] || []
})

// Load sessions from backend
const loadSessions = async () => {
  try {
    loading.value = true
    const response = await chatService.listSessions()
    sessions.value = response.data?.data || response.data || []
    
    if (sessions.value.length > 0 && !selectedSessionId.value) {
      selectedSessionId.value = sessions.value[0].id
      await loadMessages(selectedSessionId.value)
    }
  } catch (error) {
    console.error('Failed to load sessions:', error)
  } finally {
    loading.value = false
  }
}

// Load messages for a session
const loadMessages = async (sessionId) => {
  try {
    const response = await chatService.listMessages(sessionId)
    const messages = response.data?.data || response.data || []
    
    // Transform backend messages to frontend format
    const transformedMessages = messages.map(msg => ({
      id: msg.id,
      type: msg.type || 'text',
      text: msg.content || msg.text,
      senderId: msg.sender_id || msg.senderId,
      timestamp: msg.created_at || msg.timestamp,
      status: msg.status || 'sent',
      metadata: msg.metadata || {}
    }))
    
    messagesBySession.value[sessionId] = transformedMessages
  } catch (error) {
    console.error('Failed to load messages:', error)
    messagesBySession.value[sessionId] = []
  }
}

// Event handlers
const handleSessionSelected = async (sessionId) => {
  selectedSessionId.value = sessionId
  if (!messagesBySession.value[sessionId]) {
    await loadMessages(sessionId)
  }
}

const handleSendMessage = async ({ sessionId, text }) => {
  try {
    // Send message to backend
    const response = await chatService.send(sessionId, text)
    
    // Add message to local state
    const newMessage = {
      id: response.data?.id || Date.now(),
      type: 'text',
      text: text,
      senderId: currentUserId.value,
      timestamp: new Date().toISOString(),
      status: 'pending',
    }
    
    if (!messagesBySession.value[sessionId]) {
      messagesBySession.value[sessionId] = []
    }
    messagesBySession.value[sessionId].push(newMessage)
    
    // Reload messages to get backend response
    await loadMessages(sessionId)
    
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

const handleCloseChat = () => {
  console.log('Chat closed')
}

// Initialize
onMounted(async () => {
  await loadSessions()
  
  if (props.initialSessionId) {
    selectedSessionId.value = props.initialSessionId
    await loadMessages(props.initialSessionId)
  }
})
</script>

<style scoped>
.chat-widget { 
  width: 100%; 
  height: 100%;
}
</style>
