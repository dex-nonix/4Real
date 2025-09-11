<script setup>
import { ref, computed, inject, defineEmits } from 'vue';
import ChatHeader from './ChatHeader.vue';
import ChatSessionBar from './ChatSessionBar.vue';
import ChatMessageContainer from './ChatMessageContainer.vue';
import PersonaSelectionDialog from './PersonaSelectionDialog.vue';
import HistoryManagementDialog from './HistoryManagementDialog.vue';
import ProgressSpinner from 'primevue/progressspinner';
import { useToast } from 'primevue/usetoast';

// Chat component accepts external menu items
const props = defineProps({
  menuItems: { type: Array, required: false, default: () => [] }
});

const chatService = inject('chat-service');

const toast = useToast();

const emit = defineEmits(['viewHistory', 'renameHistory', 'clearMessages', 'deleteSession', 'menuItemClick']);

const chatMessageContainerRef = ref(null);


const selectedSession = ref(null);
const selectedHistory = ref(null);
const selectedPersona = ref(null);

// IDS (flat references, no nesting)
const currentSessionId = ref(null);
const currentHistoryId = ref(null);
const currentUserId = ref('user-self');

// Error handling state
const errors = ref([]);
const isLoading = ref(false);

// Dialog state
const showPersonaDialog = ref(false);
const showHistoryDialog = ref(false);

// Computed values - FLAT, NO NESTING
const currentSession = computed(() => selectedSession.value);
const currentHistory = computed(() => selectedHistory.value);
const currentPersona = computed(() => selectedPersona.value);

// Error handling utilities
const addError = (message, details = null) => {
  const error = {
    id: Date.now(),
    message,
    details,
    timestamp: new Date().toISOString()
  };
  errors.value.push(error);
  
  // Show toast notification using global toast service
  if (toast) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: message,
      life: 5000
    });
  }
  
  // Log to console
  console.error('Chat Error:', message, details);
  
  // Keep only last 10 errors
  if (errors.value.length > 10) {
    errors.value = errors.value.slice(-10);
  }
};

const addSuccess = (message) => {
  if (toast) {
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: message,
      life: 3000
    });
  }
  console.log('Chat Success:', message);
};

const addInfo = (message) => {
  if (toast) {
    toast.add({
      severity: 'info',
      summary: 'Info',
      detail: message,
      life: 3000
    });
  }
  console.log('Chat Info:', message);
};

const addWarning = (message) => {
  if (toast) {
    toast.add({
      severity: 'warn',
      summary: 'Warning',
      detail: message,
      life: 4000
    });
  }
  console.warn('Chat Warning:', message);
};

// Force refresh of messages display
const refreshMessages = async () => {
  if (chatMessageContainerRef.value && chatMessageContainerRef.value.loadMessages) {
    try {
      await chatMessageContainerRef.value.loadMessages(currentHistoryId.value);
      addInfo('Messages refreshed successfully');
    } catch (error) {
      console.error('Failed to refresh messages:', error);
      addWarning('Could not refresh messages display');
    }
  } else {
    console.error('ChatMessageContainer ref not available or loadMessages method missing');
    addError('Cannot refresh messages - component not ready');
  }
};

// Handle session selection from ChatSessionBar - FLAT DATA LOADING
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
    
    // Load FLAT session data only - NO NESTING!
    if (sessionId && chatService) {
      try {
        addInfo(`Loading session ${sessionId}...`);
        const response = await chatService.getSession(sessionId);
        console.log('Session response:', response);
        
        // Backend returns {data: {...}} - extract the actual session data
        const sessionData = response?.data || response;
        selectedSession.value = sessionData;
        console.log('Processed session data:', sessionData);
        addSuccess(`Session "${sessionData.session_name || 'Unnamed'}" loaded successfully`);
        
        // Set current history ID from session data (flat reference)
        if (sessionData.current_history_id) {
          currentHistoryId.value = sessionData.current_history_id;
          console.log('Set currentHistoryId to:', currentHistoryId.value);
          addInfo(`Using existing history: ${currentHistoryId.value}`);
        } else {
          // Create a new history if none exists
          try {
            addInfo('Creating new conversation history...');
            const historyResponse = await chatService.createHistory(sessionId, 'New Conversation');
            console.log('History creation response:', historyResponse);
            
            // Backend returns {data: {...}} - extract the actual history data
            const historyData = historyResponse?.data || historyResponse;
            if (historyData && historyData.id) {
              currentHistoryId.value = historyData.id;
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

// Handle sessions loaded from ChatSessionBar - NO GLOBAL CACHE
const handleSessionsLoaded = (sessionsList) => {
  console.log('Sessions loaded:', sessionsList);
  
  try {
    // Backend ALWAYS returns {data: [...], total: X} - extract the data array
    let actualSessions = [];
    
    if (sessionsList && sessionsList.data && Array.isArray(sessionsList.data)) {
      actualSessions = sessionsList.data;
    } else {
      console.warn('Invalid sessions response structure:', sessionsList);
      actualSessions = [];
    }
    
    // Validate sessions have proper IDs
    actualSessions = actualSessions.filter(session => {
      if (!session || typeof session.id === 'undefined' || session.id === null) {
        console.warn('Invalid session found:', session);
        return false;
      }
      return true;
    });
    
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
  }
};

// Handle session added from ChatSessionBar
const handleSessionAdded = (newSession) => {
  console.log('Session added:', newSession);
  addSuccess(`New session "${newSession.session_name || 'Unnamed'}" created successfully`);
};

// Handle message sending - OBJECT WITH MESSAGE TYPE
const handleSendMessage = async (messageData) => {
  if (!messageData?.historyId || !messageData?.content || !chatService || !currentSessionId.value) {
    addError('Cannot send message: Missing required data');
    return;
  }

  try {
    isLoading.value = true;
    addInfo('Sending message...');

    // Send payload with explicit meta-type at top-level as per contract
    const response = await chatService.sendMessage(
      currentSessionId.value,
      messageData.historyId,
      { message_type: messageData.message_type || 'user', content: messageData.content }
    );
    console.log('Message sent successfully:', response);
    addSuccess('Message sent successfully');

    // Do not refresh the full list; upsert will occur via WebSocket events

  } catch (error) {
    console.error('Failed to send message:', error);
    addError('Failed to send message', error);
  } finally {
    isLoading.value = false;
  }
};

// Handle persona addition - LAZY LOADING when dialog opens
const handleAddPersona = async () => {
  console.log('Opening persona selection dialog');
  
  try {
    // LAZY LOAD personas when dialog opens - NO GLOBAL CACHE!
    const personasData = await chatService.getPersonas();
    console.log('Personas loaded for dialog:', personasData);
    
    // Pass to dialog - NO global cache!
    showPersonaDialog.value = true;
    // Dialog component receives personasData and manages its own state
  } catch (error) {
    console.error('Failed to load personas:', error);
    addError('Failed to load personas', error);
  }
};

// Handle persona selection - FLAT DATA
const handlePersonaSelected = async (persona) => {
  try {
    isLoading.value = true;
    addInfo(`Starting chat with ${persona.name}...`);
    
    // Set selected persona (flat object)
    selectedPersona.value = persona;
    
    // Create session with persona_id (flat reference)
    const response = await chatService.startChatWithPersona(persona.id, `Chat with ${persona.name}`, persona.avatar_url);
    console.log('Persona chat started:', response);
    
    if (response) {
      const sessionData = response?.data || response;
      
      if (sessionData) {
        addSuccess(`Chat started with ${persona.name}`);

        showPersonaDialog.value = false;

        selectedSession.value = sessionData;
        currentSessionId.value = sessionData.id;

        if (sessionData.id) {
          console.log('Auto-selecting newly created session:', sessionData.id);
          await handleSessionSelected(sessionData.id);
        }
      } else {
        addError('Failed to start chat: Invalid response structure');
      }
    }
  } catch (error) {
    console.error('Failed to start chat with persona:', error);
    addError(`Failed to start chat with ${persona.name}`, error);
  } finally {
    isLoading.value = false;
  }
};

// Handle history view request - LAZY LOADING when dialog opens
const handleViewHistory = async () => {
  console.log('View history requested');
  
  if (!currentSessionId.value) {
    addError('No session selected');
    return;
  }
  
  try {
    const historiesData = await chatService.getHistories(currentSessionId.value);
    console.log('Histories loaded for dialog:', historiesData);
    
    // Pass to dialog - NO global cache!
    showHistoryDialog.value = true;
  } catch (error) {
    console.error('Failed to load histories', error);
    addError('Failed to load histories', error);
  }
};

// Handle menu item clicks from ChatHeader
const handleMenuItemClick = (item) => {
  console.log('Menu item clicked:', item.label);
  emit('menuItemClick', item);
};


// Handle history rename request - FLAT DATA
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

// Handle history selection from HistoryManagementDialog - FLAT DATA
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
    
    // Refresh messages for the new history
    await refreshMessages();
    
  } catch (error) {
    console.error('Failed to select history:', error);
    addError('Failed to select history', error);
  }
};

// Handle clear messages request
const handleClearMessages = async () => {
  if (!currentHistoryId.value) {
    addWarning('No history selected to clear messages from');
    return;
  }
  
  try {
    addInfo('Clearing all messages...');
    
    // Call the backend to clear messages for this history
    const response = await chatService.clearHistoryMessages(currentSessionId.value, currentHistoryId.value);
    
    if (response) {
      addSuccess(`Messages cleared successfully! Deleted ${response.deleted_count || 0} messages.`);
      
      // Clear the local messages display immediately
      if (chatMessageContainerRef.value && chatMessageContainerRef.value.clearLocalMessages) {
        chatMessageContainerRef.value.clearLocalMessages();
        addInfo('Messages display cleared');
      } else {
        addWarning('Could not clear messages display - manual refresh may be needed');
      }
      
    } else {
      addError('Failed to clear messages: No response from backend');
    }
    
  } catch (error) {
    console.error('Failed to clear messages:', error);
    addError('Failed to clear messages', error);
  }
};

// Handle message deletion
const handleDeleteMessage = async (deleteResult) => {
  if (deleteResult.success) {
    addSuccess('Message deleted successfully');
    console.log('Message deleted:', deleteResult.messageData);
  } else {
    addError('Failed to delete message', deleteResult.error);
    console.error('Message deletion failed:', deleteResult.error);
  }
};

// Handle session deletion from ChatHeader
const handleDeleteSession = async (deleteResult) => {
  if (deleteResult.success) {
    addSuccess('Session deleted successfully');
    console.log('Session deleted:', deleteResult.sessionId);
    
    // Clear current session state
    selectedSession.value = null;
    currentSessionId.value = null;
    currentHistoryId.value = null;
    
    // ChatSessionBar will auto-refresh when it detects the change
    addInfo('Session state cleared, sidebar will update automatically');
    
  } else {
    addError('Failed to delete session', deleteResult.error);
    console.error('Session deletion failed:', deleteResult.error);
  }
};

// Clear errors
const clearErrors = () => {
  errors.value = [];
  addInfo('Error log cleared');
};

// Delete single error
const deleteError = (errorId) => {
  const index = errors.value.findIndex(e => e.id === errorId);
  if (index !== -1) {
    errors.value.splice(index, 1);
    addSuccess('Error removed from log');
  }
};

// Copy error to clipboard
const copyError = (error) => {
  addInfo('Error details copied to clipboard');
};

// Export methods for parent components
defineExpose({
  handleSessionSelected,
  handleSessionsLoaded,
  handleSessionAdded,
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
  errors,
  isLoading
});
</script>

<template>
  <div class="flex flex-column overflow-hidden h-full w-full">
    <ChatHeader
      :persona="currentPersona"
      :current-session="currentSession"
      :current-history="currentHistory"
      :menu-items="menuItems"
      @add-persona="handleAddPersona"
      @view-history="handleViewHistory"
      @rename-history="handleRenameHistory"
      @clear-messages="handleClearMessages"
      @delete-session="handleDeleteSession"
      @menu-item-click="handleMenuItemClick"
    />

    <div class="flex flex-row flex-1" style="min-height: 0; height: 100%;">
      <ChatSessionBar
        :current-session-id="currentSessionId"
        @session-selected="handleSessionSelected"
        @add-session="handleAddPersona"
        @sessions-loaded="handleSessionsLoaded"
        @session-added="handleSessionAdded"
        @error="(errorData) => addError(errorData.message, errorData.details)"
      />

      <div class="flex-1 relative" style="height: 100%; min-height: 0;">

        <div v-if="isLoading" class="flex justify-content-center align-items-center p-4">
          <ProgressSpinner style="width: 50px; height: 50px" />
          <span class="ml-2">Loading...</span>
        </div>

        <div v-if="currentSessionId && selectedSession" class="flex-1 d-flex flex-column" style="height: 100%; min-height: 0;">
          <ChatMessageContainer
            ref="chatMessageContainerRef"
            :session-id="currentSessionId"
            :history-id="currentHistoryId"
            :current-user-id="currentUserId"
            :selected-session="selectedSession"
            :errors="errors"
            @send-message="handleSendMessage"
            @delete-message="handleDeleteMessage"
            @refresh-messages="refreshMessages"
            @error="(errorData) => addError(errorData.message, errorData.details)"
            @delete-error="deleteError"
            @clear-all-errors="clearErrors"
            @copy-error="copyError"
          />
        </div>

        <div v-if="!currentSessionId || !selectedSession" class="flex flex-column flex-1 justify-content-center align-items-center p-4">
          <i class="pi pi-spin pi-spinner text-4xl text-500 mb-3"></i>
          <p class="text-500">Select a session to start chatting...</p>
        </div>
      </div>
    </div>
    <PersonaSelectionDialog
      v-model:visible="showPersonaDialog"
      @persona-selected="handlePersonaSelected"
    />

    <HistoryManagementDialog
      v-model:visible="showHistoryDialog"
      :session-id="currentSessionId"
      :current-history-id="currentHistoryId"
      @history-selected="handleHistorySelected"
    />
  </div>
</template>
