<!-- Chat.vue -->
<script setup>
import { ref, computed, watch, inject } from 'vue';
import ChatHeader from './ChatHeader.vue';
import ChatSessionBar from './ChatSessionBar.vue';
import ChatMessageContainer from './ChatMessageContainer.vue';

// Chat component is now fully self-contained - no props needed
// It manages its own session state and can be used multiple times

// Service injection for session management
const chatService = inject('chat-runtime');

// selectedSession observable - central state for all child components
const selectedSession = ref(null);

// Sessions array - will be populated from ChatSessionBar
const sessions = ref([]);

// Current session ID - managed internally
const currentSessionId = ref(null);

// Current history ID - managed internally
const currentHistoryId = ref(null);

// Current user ID - can be configured if needed
const currentUserId = ref('user-self');

// Computed values with null safety - now using selectedSession
const currentSession = computed(() => {
  return selectedSession.value;
});

// Handle session selection from ChatSessionBar
const handleSessionSelected = async (sessionId) => {
  currentSessionId.value = sessionId;
  
  // Get full session details when session is selected
  if (sessionId && chatService) {
    try {
      const response = await chatService.getSession(sessionId);
      selectedSession.value = response.data;
      
      // Get history for the selected session
      if (response.data.histories && response.data.histories.length > 0) {
        currentHistoryId.value = response.data.histories[0].id;
      }
    } catch (error) {
      console.error('Failed to get session details:', error);
      selectedSession.value = null;
      currentHistoryId.value = null;
    }
  } else {
    selectedSession.value = null;
    currentHistoryId.value = null;
  }
};

// Handle sessions loaded from ChatSessionBar
const handleSessionsLoaded = (sessionsList) => {
  sessions.value = sessionsList;
  
  // Auto-select first session if none selected
  if (sessionsList.length > 0 && !currentSessionId.value) {
    handleSessionSelected(sessionsList[0].id);
  }
};

// Method to update selectedSession with full session object
const updateSelectedSession = (sessionObject) => {
  selectedSession.value = sessionObject;
};

const handleSendMessage = (messageData) => {
  if (!messageData?.historyId) return;
  
  // Handle message sending internally
  console.log('Message sent:', messageData);
  
  // In a real implementation, you might want to emit this to parent
  // or handle it internally depending on your needs
};

const handleAddPersona = () => {
  // Handle persona creation internally
  console.log('Add persona requested');
  
  // In a real implementation, you might want to emit this to parent
  // or handle it internally depending on your needs
};

const handleCloseChat = () => {
  // Handle chat closing internally
  console.log('Close chat requested');
  
  // In a real implementation, you might want to emit this to parent
  // or handle it internally depending on your needs
};

const handleViewHistory = () => {
  // Handle history viewing internally
  console.log('View history requested');
  
  // In a real implementation, you might want to emit this to parent
  // or handle it internally depending on your needs
};
</script>

<template>
  <div class="flex flex-column overflow-hidden" style="width: 1024px; height: 768px; border: 1px solid var(--surface-border)">
    <ChatHeader 
      :persona="currentSession?.persona" 
      :current-session="currentSession"
      @close-chat="handleCloseChat" 
      @view-history="handleViewHistory"
    />

    <div class="flex flex-row flex-1" style="min-height: 0;">
      <ChatSessionBar
        :current-session-id="currentSessionId"
        @session-selected="handleSessionSelected"
        @add-session="handleAddPersona"
        @sessions-loaded="handleSessionsLoaded"
      />
      
      <!-- Tab-based architecture: One ChatMessageContainer per session -->
      <div class="flex-1 relative">
        <div 
          v-for="session in sessions" 
          :key="session.id"
          class="chat-message-container-tab"
          :class="{ 'active-tab': selectedSession?.id === session.id }"
          :style="{ 
            display: selectedSession?.id === session.id ? 'flex' : 'none',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0
          }"
        >
          <ChatMessageContainer
            :session-id="session.id"
            :history-id="currentHistoryId"
            :current-user-id="currentUserId"
            :selected-session="session"
            @send-message="handleSendMessage"
          />
        </div>
        
        <!-- Loading state when no sessions -->
        <div v-if="sessions.length === 0" class="flex flex-column flex-1 justify-content-center align-items-center p-4">
          <i class="pi pi-spin pi-spinner text-4xl text-500 mb-3"></i>
          <p class="text-500">Loading sessions...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-message-container-tab {
  flex-direction: column;
  transition: opacity 0.2s ease;
}

.chat-message-container-tab.active-tab {
  opacity: 1;
}

.chat-message-container-tab:not(.active-tab) {
  opacity: 0;
}
</style>