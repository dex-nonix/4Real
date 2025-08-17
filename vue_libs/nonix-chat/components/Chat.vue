<!-- Chat.vue -->
<script setup>
import { ref, computed, watch, inject } from 'vue';
import ChatHeader from './ChatHeader.vue';
import ChatSessionBar from './ChatSessionBar.vue';
import ChatMessageContainer from './ChatMessageContainer.vue';

// Chat component is now fully self-contained - no props needed
// It manages its own session state and can be used multiple times

// Service injection for session management
const chatService = inject('chat-service');

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
  console.log('Session selected:', sessionId);
  
  // Prevent duplicate calls
  if (currentSessionId.value === sessionId) {
    console.log('Session already selected, skipping duplicate call');
    return;
  }
  
  currentSessionId.value = sessionId;
  
  // Get full session details when session is selected
  if (sessionId && chatService) {
    try {
      const response = await chatService.getSession(sessionId);
      console.log('Session response:', response);
      
      // Handle different response structures for session
      let sessionData;
      if (response.data && response.data.data) {
        sessionData = response.data.data;
      } else if (response.data) {
        sessionData = response.data;
      } else {
        sessionData = response;
      }
      
      selectedSession.value = sessionData;
      console.log('Processed session data:', sessionData);
      
      // Get history for the selected session
      if (sessionData.histories && sessionData.histories.length > 0) {
        currentHistoryId.value = sessionData.histories[0].id;
        console.log('Using existing history:', currentHistoryId.value);
      } else {
        // Create a new history if none exists
        try {
          const historyResponse = await chatService.createHistory(sessionId, 'New Conversation');
          console.log('History creation response:', historyResponse);
          
          // Handle different response structures
          if (historyResponse.data && historyResponse.data.id) {
            currentHistoryId.value = historyResponse.data.id;
          } else if (historyResponse.data && historyResponse.data.data && historyResponse.data.data.id) {
            currentHistoryId.value = historyResponse.data.data.id;
          } else if (historyResponse.id) {
            currentHistoryId.value = historyResponse.id;
          } else {
            console.error('Unexpected history response structure:', historyResponse);
            currentHistoryId.value = null;
          }
          
          console.log('Set currentHistoryId to:', currentHistoryId.value);
        } catch (historyError) {
          console.error('Failed to create history:', historyError);
          currentHistoryId.value = null;
        }
      }
      
      console.log('Final state - selectedSession:', selectedSession.value, 'currentHistoryId:', currentHistoryId.value);
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
  console.log('Sessions loaded:', sessionsList);
  sessions.value = sessionsList;
  
  // Auto-select first session if none selected
  if (sessionsList.length > 0 && !currentSessionId.value) {
    console.log('Auto-selecting first session:', sessionsList[0].id);
    handleSessionSelected(sessionsList[0].id);
  }
};

// Watch for currentHistoryId changes to ensure ChatMessageContainer gets updates
watch(currentHistoryId, (newHistoryId) => {
  console.log('currentHistoryId changed to:', newHistoryId);
});

// Method to update selectedSession with full session object
const updateSelectedSession = (sessionObject) => {
  selectedSession.value = sessionObject;
};

const handleSendMessage = async (messageData) => {
  if (!messageData?.historyId || !chatService) return;
  
  try {
    // Send message using the chat service
    const response = await chatService.sendMessageToHistory(messageData.historyId, messageData.text);
    console.log('Message sent successfully:', response);
    
    // Refresh the current session to get updated data
    if (currentSessionId.value) {
      await handleSessionSelected(currentSessionId.value);
    }
  } catch (error) {
    console.error('Failed to send message:', error);
  }
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
        <!-- Debug info -->
        <div v-if="true" class="p-2 surface-100 text-xs">
          Debug: currentSessionId={{ currentSessionId }}, currentHistoryId={{ currentHistoryId }}, sessions={{ sessions.length }}, selectedSession={{ selectedSession?.id }}
        </div>
        
        <div 
          v-for="session in sessions" 
          :key="session.id"
          class="chat-message-container-tab"
          :class="{ 'active-tab': currentSessionId === session.id }"
          :style="{ 
            display: currentSessionId === session.id ? 'flex' : 'none',
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
            :selected-session="selectedSession"
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