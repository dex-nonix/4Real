<!-- Chat.vue -->
<script setup>
import { ref, computed, watch, inject } from 'vue';
import ChatHeader from './ChatHeader.vue';
import ChatSessionBar from './ChatSessionBar.vue';
import ChatMessageContainer from './ChatMessageContainer.vue';
import PersonaSelectionDialog from './PersonaSelectionDialog.vue';
import HistoryManagementDialog from './HistoryManagementDialog.vue';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';

// Chat component is now fully self-contained - no props needed
// It manages its own session state and can be used multiple times

// Toast service for user feedback
const toast = useToast();

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

// Error handling state
const errors = ref([]);
const isLoading = ref(false);

// Dialog state
const showPersonaDialog = ref(false);
const showHistoryDialog = ref(false);

// Computed values with null safety - now using selectedSession
const currentSession = computed(() => {
  return selectedSession.value;
});

// Get current history object from selectedSession and currentHistoryId
const currentHistory = computed(() => {
  if (!selectedSession.value?.histories || !currentHistoryId.value) {
    return null;
  }
  
  // Find the current history in the selected session's histories
  return selectedSession.value.histories.find(history => history.id === currentHistoryId.value) || null;
});

// Get current persona object for ChatHeader
const currentPersona = computed(() => {
  if (currentSession.value?.persona) {
    return currentSession.value.persona;
  }
  
  // Fallback: create persona object from session data
  if (currentSession.value?.persona_id && currentSession.value?.session_name) {
    return {
      id: currentSession.value.persona_id,
      name: currentSession.value.session_name,
      avatar_url: currentSession.value.avatar_url || null
    };
  }
  
  return null;
});

// Error handling utilities
const addError = (message, details = null) => {
  const error = {
    id: Date.now(),
    message,
    details,
    timestamp: new Date().toISOString()
  };
  errors.value.push(error);
  
  // Show toast notification
  toast.add({
    severity: 'error',
    summary: 'Error',
    detail: message,
    life: 5000
  });
  
  // Log to console
  console.error('Chat Error:', message, details);
  
  // Keep only last 10 errors
  if (errors.value.length > 10) {
    errors.value = errors.value.slice(-10);
  }
};

const addSuccess = (message) => {
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: message,
    life: 3000
  });
  console.log('Chat Success:', message);
};

const addInfo = (message) => {
  toast.add({
    severity: 'info',
    summary: 'Info',
    detail: message,
    life: 3000
  });
  console.log('Chat Info:', message);
};

const addWarning = (message) => {
  toast.add({
    severity: 'warn',
    summary: 'Warning',
    detail: message,
    life: 4000
  });
  console.warn('Chat Warning:', message);
};

// Handle session selection from ChatSessionBar
const handleSessionSelected = async (sessionId) => {
  console.log('Session selected:', sessionId);
  
  // Prevent duplicate calls
  if (currentSessionId.value === sessionId) {
    console.log('Session already selected, skipping duplicate call');
    addInfo('Session already selected');
    return;
  }
  
  // Prevent selection of invalid session IDs
  if (!sessionId || typeof sessionId === 'undefined' || sessionId === null) {
    console.warn('Invalid session ID provided:', sessionId);
    addWarning('Invalid session ID provided');
    return;
  }
  
  try {
    isLoading.value = true;
    currentSessionId.value = sessionId;
    
    // Get full session details when session is selected
    if (sessionId && chatService) {
      try {
        addInfo(`Loading session ${sessionId}...`);
        const response = await chatService.getSession(sessionId);
        console.log('Session response:', response);
        
        let sessionData = response;
        
        selectedSession.value = sessionData;
        console.log('Processed session data:', sessionData);
        addSuccess(`Session "${sessionData.session_name || 'Unnamed'}" loaded successfully`);
        
        // Get history for the selected session
        if (sessionData.histories && sessionData.histories.length > 0) {
          currentHistoryId.value = sessionData.histories[0].id;
          console.log('Using existing history:', currentHistoryId.value);
          addInfo(`Using existing history: ${sessionData.histories[0].title || 'Untitled'}`);
        } else {
          // Create a new history if none exists
          try {
            addInfo('Creating new conversation history...');
            const historyResponse = await chatService.createHistory(sessionId, 'New Conversation');
            console.log('History creation response:', historyResponse);
            
            if (historyResponse && historyResponse.id) {
              currentHistoryId.value = historyResponse.id;
            } else {
              console.error('Unexpected history response structure:', historyResponse);
              currentHistoryId.value = null;
              addError('Failed to create history: Invalid response structure', historyResponse);
            }
            
            if (currentHistoryId.value) {
              console.log('Set currentHistoryId to:', currentHistoryId.value);
              addSuccess('New conversation history created successfully');
            }
          } catch (historyError) {
            console.error('Failed to create history:', historyError);
            addError('Failed to create conversation history', historyError);
            currentHistoryId.value = null;
          }
        }
        
        console.log('Final state - selectedSession:', selectedSession.value, 'currentHistoryId:', currentHistoryId.value);
      } catch (error) {
        console.error('Failed to get session details:', error);
        addError('Failed to load session details', error);
        selectedSession.value = null;
        currentHistoryId.value = null;
      }
    } else {
      selectedSession.value = null;
      currentHistoryId.value = null;
      addWarning('No chat service available or invalid session ID');
    }
  } catch (error) {
    console.error('Session selection failed:', error);
    addError('Session selection failed', error);
  } finally {
    isLoading.value = false;
  }
};

// Handle sessions loaded from ChatSessionBar
const handleSessionsLoaded = (sessionsList) => {
  console.log('Sessions loaded:', sessionsList);
  
  try {
    let actualSessions = sessionsList || [];
    
    // Validate sessions have proper IDs
    actualSessions = actualSessions.filter(session => {
      if (!session || typeof session.id === 'undefined' || session.id === null) {
        console.warn('Invalid session found:', session);
        return false;
      }
      return true;
    });
    
    sessions.value = actualSessions;
    console.log('Processed and validated sessions:', actualSessions);
    
    if (actualSessions.length === 0) {
      addInfo('No valid chat sessions found');
    } else {
      addInfo(`Loaded ${actualSessions.length} valid chat session(s)`);
      
      // Auto-select first session if none selected
      if (!currentSessionId.value) {
        console.log('Auto-selecting first session:', actualSessions[0].id);
        handleSessionSelected(actualSessions[0].id);
      }
    }
  } catch (error) {
    console.error('Error processing sessions:', error);
    addError('Failed to process sessions', error);
    sessions.value = [];
  }
};

// Handle session added from ChatSessionBar
const handleSessionAdded = (newSession) => {
  console.log('Session added:', newSession);
  addSuccess(`New session "${newSession.session_name || 'Unnamed'}" created successfully`);
};

// Handle session removed from ChatSessionBar
const handleSessionRemoved = (sessionId) => {
  console.log('Session removed:', sessionId);
  addSuccess('Session removed successfully');
  
  // If the removed session was selected, clear selection
  if (currentSessionId.value === sessionId) {
    selectedSession.value = null;
    currentHistoryId.value = null;
    currentSessionId.value = null;
    addInfo('Current session cleared');
  }
};

// Handle message sending
const handleSendMessage = async (messageData) => {
  if (!messageData?.historyId || !chatService || !currentSessionId.value) {
    addError('Cannot send message: Missing required data');
    return;
  }
  
  try {
    isLoading.value = true;
    addInfo('Sending message...');
    
    // Send message using the chat service (now requires sessionId and historyId)
    const response = await chatService.sendMessageToHistory(currentSessionId.value, messageData.historyId, messageData.text);
    console.log('Message sent successfully:', response);
    addSuccess('Message sent successfully');
    
    // Refresh the current session to get updated data
    if (currentSessionId.value) {
      await handleSessionSelected(currentSessionId.value);
    }
  } catch (error) {
    console.error('Failed to send message:', error);
    addError('Failed to send message', error);
  } finally {
    isLoading.value = false;
  }
};

// Handle persona addition - open persona selection dialog
const handleAddPersona = () => {
  console.log('Opening persona selection dialog');
  showPersonaDialog.value = true;
};

// Refresh sessions list from ChatSessionBar
const refreshSessions = async () => {
  try {
    addInfo('Refreshing sessions...');
    // Manually trigger a reload by calling the service
    const response = await chatService.getSessions();
    if (response) {
      handleSessionsLoaded(response);
      console.log('Sessions refreshed via service call');
    }
  } catch (error) {
    console.error('Failed to refresh sessions:', error);
    addError('Failed to refresh sessions', error);
  }
};

// Handle persona selection
const handlePersonaSelected = async (persona) => {
  try {
    isLoading.value = true;
    addInfo(`Starting chat with ${persona.name}...`);
    
    const response = await chatService.startChatWithPersona(persona.id, `Chat with ${persona.name}`, persona.avatar_url);
    console.log('Persona chat started:', response);
    
    if (response) {
      addSuccess(`Chat started with ${persona.name}`);
      
      // Close the persona dialog
      showPersonaDialog.value = false;
      
      // Refresh sessions to show the new one
      await refreshSessions();
      
      // Auto-select the new session if it was created
      if (response.id) {
        console.log('Auto-selecting newly created session:', response.id);
        await handleSessionSelected(response.id);
      }
    }
  } catch (error) {
    console.error('Failed to start chat with persona:', error);
    addError(`Failed to start chat with ${persona.name}`, error);
  } finally {
    isLoading.value = false;
  }
};

// Handle history view request
const handleViewHistory = () => {
  console.log('View history requested');
  showHistoryDialog.value = true;
};

// Handle chat close request
const handleCloseChat = () => {
  console.log('Close chat requested');
  addInfo('Close chat functionality not yet implemented');
};

// Handle history rename request
const handleRenameHistory = async (historyId, newTitle) => {
  try {
    if (!currentSessionId.value) {
      addError('No session selected for history rename');
      return;
    }
    
    addInfo('Renaming history...');
    const response = await chatService.updateHistory(currentSessionId.value, historyId, { title: newTitle });
    
    if (response) {
      addSuccess('History renamed successfully');
      // Refresh the current session to get updated data
      await handleSessionSelected(currentSessionId.value);
    }
  } catch (error) {
    console.error('Failed to rename history:', error);
    addError('Failed to rename history', error);
  }
};

// Handle history selection from HistoryManagementDialog
const handleHistorySelected = async (historyId) => {
  try {
    if (!currentSessionId.value) {
      addError('No session selected for history selection');
      return;
    }
    
    console.log('History selected:', historyId);
    currentHistoryId.value = historyId;
    
    // Close the history dialog
    showHistoryDialog.value = false;
    
    addSuccess('History selected successfully');
  } catch (error) {
    console.error('Failed to select history:', error);
    addError('Failed to select history', error);
  }
};

// Handle clear messages request
const handleClearMessages = () => {
  if (!currentHistoryId.value) {
    addWarning('No history selected to clear messages from');
    return;
  }
  
  addInfo('Clear messages functionality not yet implemented');
};

// Clear errors
const clearErrors = () => {
  errors.value = [];
  addInfo('Error log cleared');
};

// Export methods for parent components
defineExpose({
  handleSessionSelected,
  handleSessionsLoaded,
  handleSessionAdded,
  handleSessionRemoved,
  handleSendMessage,
  handleAddPersona,
  handlePersonaSelected,
  clearErrors,
  currentSession,
  currentPersona,
  currentHistory,
  currentSessionId,
  currentHistoryId,
  selectedSession,
  sessions,
  errors,
  isLoading
});
</script>

<template>
  <!-- Toast notifications for user feedback -->
  <Toast />
  
  <div class="flex flex-column overflow-hidden" style="width: 1024px; height: 768px; border: 1px solid var(--surface-border)">
    <ChatHeader 
      :persona="currentPersona" 
      :current-session="currentSession"
      :current-history="currentHistory"
      @add-persona="handleAddPersona"
      @view-history="handleViewHistory"
      @close-chat="handleCloseChat"
      @rename-history="handleRenameHistory"
      @clear-messages="handleClearMessages"
    />

    <div class="flex flex-row flex-1" style="min-height: 0;">
      <ChatSessionBar
        :current-session-id="currentSessionId"
        @session-selected="handleSessionSelected"
        @add-session="handleAddPersona"
        @sessions-loaded="handleSessionsLoaded"
        @session-added="handleSessionAdded"
        @session-removed="handleSessionRemoved"
        @error="(errorData) => addError(errorData.message, errorData.details)"
      />
      
      <!-- Tab-based architecture: One ChatMessageContainer per session -->
      <div class="flex-1 relative">
        <!-- Debug info -->
        <div v-if="true" class="p-2 surface-100 text-xs">
          Debug: currentSessionId={{ currentSessionId }}, currentHistoryId={{ currentHistoryId }}, sessions={{ sessions.length }}, selectedSession={{ selectedSession?.id }}
        </div>
        
        <!-- Error display -->
        <div v-if="errors.length > 0" class="p-2 surface-100 border-round">
          <div class="flex align-items-center justify-content-between mb-2">
            <h4 class="m-0 text-red-500">Errors ({{ errors.length }})</h4>
            <Button label="Clear" size="small" severity="secondary" @click="clearErrors" />
          </div>
          <div v-for="error in errors.slice(-3)" :key="error.id" class="p-2 mb-2 surface-200 border-round">
            <div class="text-red-600 font-semibold">{{ error.message }}</div>
            <div v-if="error.details" class="text-xs text-500 mt-1">
              {{ typeof error.details === 'object' ? JSON.stringify(error.details, null, 2) : error.details }}
            </div>
            <div class="text-xs text-400 mt-1">{{ new Date(error.timestamp).toLocaleTimeString() }}</div>
          </div>
        </div>
        
        <!-- Loading indicator -->
        <div v-if="isLoading" class="flex justify-content-center align-items-center p-4">
          <ProgressSpinner style="width: 50px; height: 50px" />
          <span class="ml-2">Loading...</span>
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
            v-if="session.id && currentSessionId && selectedSession"
            :session-id="session.id"
            :history-id="currentHistoryId"
            :current-user-id="currentUserId"
            :selected-session="selectedSession"
            @send-message="handleSendMessage"
            @error="(errorData) => addError(errorData.message, errorData.details)"
          />
        </div>
        
        <!-- Loading state when no sessions or sessions are being processed -->
        <div v-if="sessions.length === 0 || isLoading" class="flex flex-column flex-1 justify-content-center align-items-center p-4">
          <i class="pi pi-spin pi-spinner text-4xl text-500 mb-3"></i>
          <p class="text-500">{{ isLoading ? 'Processing...' : 'Loading sessions...' }}</p>
        </div>
      </div>
    </div>
    
    <!-- Persona Selection Dialog -->
    <PersonaSelectionDialog
      v-model:visible="showPersonaDialog"
      @persona-selected="handlePersonaSelected"
    />
    
    <!-- History Management Dialog -->
    <HistoryManagementDialog
      v-model:visible="showHistoryDialog"
      :session-id="currentSessionId"
      :current-history-id="currentHistoryId"
      @history-selected="handleHistorySelected"
    />
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