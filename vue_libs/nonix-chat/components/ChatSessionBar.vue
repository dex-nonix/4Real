<!-- ChatSessionBar.vue -->
<script setup>
import { ref, onMounted, inject } from 'vue';
import Button from 'primevue/button';
import Divider from 'primevue/divider';
import Avatar from 'primevue/avatar';

const props = defineProps({
  currentSessionId: { type: [String, Number, null], required: false, default: null }
});

const emit = defineEmits(['session-selected', 'session-added', 'session-removed', 'sessions-loaded', 'error', 'add-session']);

// Service injection
const chatService = inject('chat-service');

// State management - self-contained
const sessions = ref([]);
const loading = ref(false);

// Load sessions on mount
onMounted(async () => {
  await loadSessions();
});

// Load all sessions
const loadSessions = async () => {
  try {
    loading.value = true;
    const response = await chatService.getSessions();
    console.log('Raw sessions response:', response);
    
    // Backend returns {data: [...], total: X} - extract just the data array
    const sessionsData = response?.data || [];
    sessions.value = sessionsData;
    console.log('Processed sessions in ChatSessionBar:', sessionsData);
    
    // Emit sessions loaded event for tab-based architecture - send the FULL response
    emit('sessions-loaded', response);
    
    // Don't auto-select here - let parent handle it
  } catch (error) {
    console.error('Failed to load sessions:', error);
    sessions.value = [];
    // Emit empty response structure even on error
    emit('sessions-loaded', { data: [], total: 0 });
    // Emit error for parent component
    emit('error', {
      message: 'Failed to load sessions',
      details: error
    });
  } finally {
    loading.value = false;
  }
};

// Create new session
const createSession = async (personaId, sessionName) => {
  try {
    const response = await chatService.createSession(personaId, sessionName);
    const newSession = response;
    
    // Add to local sessions
    sessions.value.push(newSession);
    
    // Emit session added event
    emit('session-added', newSession);
    
    // Select the new session
    emit('session-selected', newSession.id);
    
    return newSession;
  } catch (error) {
    console.error('Failed to create session:', error);
    emit('error', {
      message: 'Failed to create session',
      details: error
    });
    throw error;
  }
};

// Delete session
const deleteSession = async (sessionId) => {
  try {
    await chatService.deleteSession(sessionId);
    
    // Remove from local sessions
    const index = sessions.value.findIndex(s => s.id === sessionId);
    if (index !== -1) {
      sessions.value.splice(index, 1);
    }
    
    // Emit session removed event
    emit('session-removed', sessionId);
    
    return true;
  } catch (error) {
    console.error('Failed to delete session:', error);
    emit('error', {
      message: 'Failed to delete session',
      details: error
    });
    throw error;
  }
};

// Update session
const updateSession = async (sessionId, data) => {
  try {
    const response = await chatService.updateSession(sessionId, data);
    const updatedSession = response;
    
    // Update local session
    const index = sessions.value.findIndex(s => s.id === sessionId);
    if (index !== -1) {
      sessions.value[index] = updatedSession;
    }
    
    return updatedSession;
  } catch (error) {
    console.error('Failed to update session:', error);
    emit('error', {
      message: 'Failed to update session',
      details: error
    });
    throw error;
  }
};

const getAvatarDisplay = (session) => {
  if (!session) return { image: null, fallback: '??' };
  
  if (session.avatar_url) {
    return { image: session.avatar_url, fallback: null };
  }
  
  // Use session name for initials since we have flat sessions
  const name = session.session_name || '??';
  const initials = name.substring(0, 2).toUpperCase();
  return { image: null, fallback: initials };
};

// Handle session selection
const handleSessionSelected = (sessionId) => {
  emit('session-selected', sessionId);
};

// Handle add session (opens persona selection)
const handleAddSession = () => {
  emit('add-session');
};

// Expose methods for parent component
defineExpose({
  loadSessions,
  createSession,
  deleteSession,
  updateSession
});
</script>

<template>
  <aside class="h-full surface-section flex-shrink-0 surface-border select-none">
    <div class="flex flex-column h-full">
      <div class="flex flex-column flex-grow-1 overflow-y-auto">
        <div v-if="loading" class="p-3 text-center">
          <i class="pi pi-spin pi-spinner text-2xl"></i>
          <p class="mt-2 text-sm">Loading sessions...</p>
        </div>
        <div v-else-if="sessions.length === 0" class="no-sessions p-3 text-center">
          <span class="text-500 text-sm">No sessions available</span>
        </div>
        <div 
          v-for="session in sessions" 
          :key="session.id" 
          class="session-item cursor-pointer p-3 hover:surface-200"
          :class="{ 'selected-session': currentSessionId === session.id }"
          @click="handleSessionSelected(session.id)"
        >
          <Avatar 
            :image="getAvatarDisplay(session).image" 
            :label="getAvatarDisplay(session).fallback"
            size="large" 
            shape="circle"
          />
        </div>
      </div>

      <div class="mt-auto flex-shrink-0">
        <Divider class="mb-1"/>
        <div class="p-2 mx-auto">
          <Button
            icon="pi pi-plus"
            rounded
            severity="secondary"
            @click="handleAddSession"
            v-tooltip.bottom="'Add New Session'"
          />
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.session-item {
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: 1px solid var(--surface-border);
  transition: all 0.2s ease;
}

.session-item:hover {
  background-color: var(--surface-200);
}

.selected-session {
  background-color: var(--primary-color);
  color: var(--primary-color-text);
}

.selected-session:hover {
  background-color: var(--primary-600);
}
</style>
