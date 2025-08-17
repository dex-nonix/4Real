# FRONTEND INTEGRATION - CORRECT IMPLEMENTATION

## OVERVIEW
This document outlines the correct frontend changes needed to work with the backend models that are ALREADY CORRECT.

## BACKEND MODELS ARE PERFECT (DON'T CHANGE THEM)

The backend models already support exactly what you want:
- **ChatSession** - has persona_id, session_name, session_icon, current_history_id
- **ChatHistory** - conversation threads within sessions
- **ChatMessage** - messages within histories
- **Persona** - AI characters with optional avatar_url

## FRONTEND CHANGES NEEDED

### 1. UPDATE ChatRuntimeService.js

**Replace the entire service with new methods:**

```javascript
export default class ChatRuntimeService extends BaseApiService {
  basePath() { return '/chat' }

  // Get all personas with their sessions
  getPersonas() {
    return this.get('/personas')
  }

  // Get all sessions for a specific persona
  getSessions(personaId) {
    return this.get(`/personas/${encodeURIComponent(personaId)}/sessions`)
  }

  // Create new session with persona
  createSession(personaId, sessionName, sessionIcon) {
    return this.post(`/personas/${encodeURIComponent(personaId)}/start-chat`, {
      session_name: sessionName,
      session_icon: sessionIcon
    })
  }

  // Get histories within a session
  getHistories(sessionId) {
    return this.get(`/chat-sessions/${encodeURIComponent(sessionId)}/histories`)
  }

  // Create new history within session
  createHistory(sessionId, title) {
    return this.post(`/chat-sessions/${encodeURIComponent(sessionId)}/histories`, {
      title: title
    })
  }

  // Get messages from specific history
  getHistoryMessages(historyId) {
    return this.get(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}/messages`)
  }

  // Send message to specific history
  sendMessageToHistory(historyId, content) {
    return this.post(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}/send`, {
      content: content
    })
  }

  // Activate a different history
  activateHistory(sessionId, historyId) {
    return this.post(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}/activate`)
  }

  // Update history (rename)
  updateHistory(sessionId, historyId, title, summary) {
    return this.put(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}`, {
      title: title,
      summary: summary
    })
  }

  // Delete history
  deleteHistory(sessionId, historyId) {
    return this.delete(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}`)
  }

  // Legacy methods (keep for compatibility)
  listSessions(params = {}) {
    return this.get('/chat-sessions', { query: params })
  }

  getSession(id) {
    return this.get(`/chat-sessions/${encodeURIComponent(id)}`)
  }

  send(sessionId, content) {
    return this.post(`/chat-sessions/${encodeURIComponent(sessionId)}/send`, { content })
  }
}
```

### 2. UPDATE Chat.vue (Main Container)

**Change props and state:**

```vue
<script setup>
import { ref, computed } from 'vue';
import ChatHeader from './ChatHeader.vue';
import ChatSessionBar from './ChatSessionBar.vue';
import ChatMessages from './ChatMessages.vue';
import ChatMessageInput from './ChatMessageInput.vue';

const props = defineProps({
  personas: { type: Array, required: true },  // Changed from sessions
  currentPersonaId: { type: [String, Number], required: true },
  currentSessionId: { type: [String, Number], required: true },
  currentHistoryId: { type: [String, Number], required: true }
});

const emit = defineEmits(['personaSelected', 'sessionSelected', 'historySelected', 'sendMessage', 'closeChat']);

// Computed values
const currentPersona = computed(() => {
  return props.personas.find(p => p.id === props.currentPersonaId);
});

const currentSession = computed(() => {
  return currentPersona.value?.sessions.find(s => s.id === props.currentSessionId);
});

const currentHistory = computed(() => {
  return currentSession.value?.histories.find(h => h.id === props.currentHistoryId);
});

const handlePersonaSelected = (personaId) => {
  emit('personaSelected', personaId);
};

const handleSessionSelected = (sessionId) => {
  emit('sessionSelected', sessionId);
};

const handleHistorySelected = (historyId) => {
  emit('historySelected', historyId);
};

const handleSendMessage = (messageText) => {
  emit('sendMessage', {
    historyId: props.currentHistoryId,
    text: messageText,
  });
};
</script>

<template>
  <div class="flex flex-column overflow-hidden" style="width: 1024px; height: 768px; border: 1px solid var(--surface-border)">
    <ChatHeader 
      :persona="currentPersona" 
      :current-session="currentSession"
      :current-history="currentHistory"
      @close-chat="emit('closeChat')" 
    />

    <div class="flex flex-row flex-1" style="min-height: 0;">
      <ChatSessionBar
        :personas="personas"
        :current-persona-id="currentPersonaId"
        :current-session-id="currentSessionId"
        @persona-selected="handlePersonaSelected"
        @session-selected="handleSessionSelected"
      />
      <div class="flex flex-column flex-1">
        <ChatMessages
          :messages="currentHistory?.messages || []"
          :current-user-id="currentUserId"
        />
        <ChatMessageInput v-model="newMessage" @send-message="handleSendMessage" />
      </div>
    </div>
  </div>
</template>
```

### 3. UPDATE ChatHeader.vue

**Change props and add history management:**

```vue
<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import { ref } from 'vue';

const props = defineProps({
  persona: { type: Object, required: true },
  currentSession: { type: Object, required: true },
  currentHistory: { type: Object, required: true }
});

const emit = defineEmits(['viewHistory', 'closeChat', 'renameHistory']);

const isEditingTitle = ref(false);
const editedTitle = ref('');

const startEditing = () => {
  editedTitle.value = props.currentHistory.title;
  isEditingTitle.value = true;
};

const saveTitle = () => {
  emit('renameHistory', props.currentHistory.id, editedTitle.value);
  isEditingTitle.value = false;
};

const cancelEditing = () => {
  isEditingTitle.value = false;
};

// Avatar fallback logic
const getAvatarDisplay = () => {
  if (props.persona.avatar_url) {
    return { image: props.persona.avatar_url, fallback: null };
  }
  // Use first 2 characters of persona name
  const initials = props.persona.name.substring(0, 2).toUpperCase();
  return { image: null, fallback: initials };
};
</script>

<template>
  <header class="flex justify-content-between align-items-center surface-section border-bottom-1 surface-border flex-shrink-0" style="height: 60px;">
    <div class="flex align-items-center gap-3">
      <Avatar 
        class="m-2" 
        :image="getAvatarDisplay().image" 
        :label="getAvatarDisplay().fallback"
        size="large" 
        shape="circle" 
      />
      <div class="flex flex-column">
        <span class="font-bold text-900">{{ persona.name }}</span>
        <div v-if="!isEditingTitle" class="text-sm text-500 cursor-pointer" @click="startEditing">
          {{ currentHistory.title }}
        </div>
        <div v-else class="flex align-items-center gap-2">
          <input 
            v-model="editedTitle" 
            @keyup.enter="saveTitle"
            @keyup.esc="cancelEditing"
            class="p-inputtext p-inputtext-sm"
            style="width: 200px;"
          />
          <Button icon="pi pi-check" size="small" @click="saveTitle" />
          <Button icon="pi pi-times" size="small" severity="secondary" @click="cancelEditing" />
        </div>
      </div>
    </div>

    <div class="flex align-items-center gap-1">
      <Button icon="pi pi-history" text rounded severity="secondary" @click="emit('viewHistory')" v-tooltip.bottom="'View History'" />
      <Button icon="pi pi-times" text rounded severity="secondary" @click="emit('closeChat')" v-tooltip.bottom="'Close Chat'"/>
    </div>
  </header>
</template>
```

### 4. UPDATE ChatSessionBar.vue

**Change to show personas with sessions:**

```vue
<script setup>
import Button from 'primevue/button';
import Divider from 'primevue/divider';
import Avatar from 'primevue/avatar';
import { ref } from 'vue';

const props = defineProps({
  personas: { type: Array, required: true },
  currentPersonaId: { type: [String, Number], required: true },
  currentSessionId: { type: [String, Number], required: true }
});

const emit = defineEmits(['personaSelected', 'sessionSelected', 'addPersona']);

const expandedPersonas = ref(new Set());

const togglePersona = (personaId) => {
  if (expandedPersonas.value.has(personaId)) {
    expandedPersonas.value.delete(personaId);
  } else {
    expandedPersonas.value.add(personaId);
  }
};

const getAvatarDisplay = (persona) => {
  if (persona.avatar_url) {
    return { image: persona.avatar_url, fallback: null };
  }
  const initials = persona.name.substring(0, 2).toUpperCase();
  return { image: null, fallback: initials };
};
</script>

<template>
  <aside class="h-full surface-section flex-shrink-0 surface-border select-none">
    <div class="flex flex-column h-full">
      <div class="flex flex-column flex-grow-1 overflow-y-auto">
        <div v-for="persona in personas" :key="persona.id" class="persona-section">
          <!-- Persona Header -->
          <div 
            class="persona-header cursor-pointer p-2 hover:surface-200"
            :class="{ 'surface-200': currentPersonaId === persona.id }"
            @click="togglePersona(persona.id)"
          >
            <div class="flex align-items-center gap-2">
              <Avatar 
                :image="getAvatarDisplay(persona).image" 
                :label="getAvatarDisplay(persona).fallback"
                size="large" 
                shape="circle"
              />
              <div class="flex flex-column flex-grow-1">
                <span class="font-bold text-sm">{{ persona.name }}</span>
                <span class="text-xs text-500">{{ persona.sessions.length }} sessions</span>
              </div>
              <i class="pi" :class="expandedPersonas.has(persona.id) ? 'pi-chevron-down' : 'pi-chevron-right'"></i>
            </div>
          </div>

          <!-- Sessions for this persona -->
          <div v-if="expandedPersonas.has(persona.id)" class="sessions-list">
            <div 
              v-for="session in persona.sessions" 
              :key="session.id"
              class="session-item cursor-pointer p-2 pl-4 hover:surface-100"
              :class="{ 'surface-100 border-left-2 border-blue-500': currentSessionId === session.id }"
              @click="emit('sessionSelected', session.id)"
            >
              <div class="flex align-items-center gap-2">
                <span v-if="session.session_icon" class="text-lg">{{ session.session_icon }}</span>
                <span class="text-sm">{{ session.session_name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-auto flex-shrink-0">
        <Divider class="mb-1"/>
        <div class="p-2 mx-auto">
          <Button
            icon="pi pi-plus"
            rounded
            severity="secondary"
            @click="emit('addPersona')"
            v-tooltip.bottom="'Add New Persona Chat'"
          />
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.persona-section {
  border-bottom: 1px solid var(--surface-border);
}

.persona-header:hover {
  background-color: var(--surface-100);
}

.sessions-list {
  background-color: var(--surface-50);
}

.session-item:hover {
  background-color: var(--surface-100);
}
</style>
```

### 5. UPDATE ChatMessages.vue

**Update to work with history-based messages:**

```vue
<script setup>
import { computed, onMounted } from 'vue';
import chatMessageTypeManager from './ChatMessageTypeManager.js';
import TextMessage from './message-types/TextMessage.vue';
import SystemMessage from './message-types/SystemMessage.vue';
import ToolMessage from './message-types/ToolMessage.vue';
import UserMessage from './message-types/UserMessage.vue';

const props = defineProps({
  messages: {
    type: Array,
    required: true,
    default: () => []
  },
  currentUserId: {
    type: [String, Number],
    required: true
  }
});

// Register all message types with the manager
onMounted(() => {
  chatMessageTypeManager.registerMessageType('text', TextMessage);
  chatMessageTypeManager.registerMessageType('system', SystemMessage);
  chatMessageTypeManager.registerMessageType('tool', ToolMessage);
  chatMessageTypeManager.registerMessageType('user', UserMessage);
});

// Get the appropriate component for each message
const getMessageComponent = (message) => {
  const messageType = message.message_type || 'text';
  return chatMessageTypeManager.getMessageType(messageType);
};

// Check if message has a valid type
const hasValidMessageType = (message) => {
  const messageType = message.message_type || 'text';
  return chatMessageTypeManager.hasMessageType(messageType);
};
</script>

<template>
  <div class="flex-1 p-4 overflow-y-auto surface-ground">
    <div v-if="messages.length === 0" class="text-center text-color-secondary p-4">
      <i class="pi pi-comments text-4xl mb-2"></i>
      <p>No messages yet. Start a conversation!</p>
    </div>
    
    <div v-else v-for="message in messages" :key="message.id">
      <component
        :is="getMessageComponent(message)"
        v-if="hasValidMessageType(message)"
        :message="message"
        :currentUserId="currentUserId"
      />
      <div v-else class="p-3 text-center text-color-secondary">
        <i class="pi pi-exclamation-triangle mr-2"></i>
        Unknown message type: {{ message.message_type || 'undefined' }}
      </div>
    </div>
  </div>
</template>
```

### 6. UPDATE ChatMessageInput.vue

**Add history context awareness:**

```vue
<script setup>
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';

const message = defineModel();

const props = defineProps({
  currentHistoryId: { type: [String, Number], required: true },
  availableTools: { type: Array, default: () => [] }
});

const emit = defineEmits(['sendMessage', 'regenerateResponse', 'showTools']);

const onSend = () => {
  if (message.value?.trim() && props.currentHistoryId) {
    emit('sendMessage', message.value);
    message.value = '';
  }
};

const showTools = () => {
  emit('showTools');
};
</script>

<template>
  <div class="flex align-items-center p-1 border-top-1 surface-border surface-section flex-shrink-0">
    <Button 
      icon="pi pi-box" 
      text 
      rounded 
      severity="secondary"
      @click="showTools"
      v-tooltip.bottom="'Available Tools'"
    />

    <span class="p-input-icon-right flex-grow-1 mx-2">
      <IconField>
        <InputText
          v-model="message"
          placeholder="Type a message..."
          class="w-full"
          @keyup.enter="onSend"
          :disabled="!currentHistoryId"
        />
        <InputIcon class="pi pi-send" @click="onSend" />
      </IconField>
    </span>

    <div class="flex align-items-center gap-2">
      <Button icon="pi pi-ellipsis-h" text rounded severity="secondary"/>
    </div>
  </div>
</template>
```

### 7. NEW COMPONENTS NEEDED

#### 7.1 PersonaSelectionDialog.vue
```vue
<template>
  <Dialog 
    v-model:visible="visible" 
    modal 
    header="Select Persona to Chat With"
    :style="{ width: '600px' }"
  >
    <div class="personas-grid">
      <div 
        v-for="persona in personas" 
        :key="persona.id"
        class="persona-card cursor-pointer p-3 border-round surface-border border-1 hover:surface-100"
        @click="selectPersona(persona)"
      >
        <Avatar 
          :image="persona.avatar_url" 
          :label="persona.name.substring(0, 2).toUpperCase()"
          size="large" 
          shape="circle"
        />
        <h3 class="mt-2 mb-1">{{ persona.name }}</h3>
        <p class="text-sm text-500">{{ persona.system_prompt?.substring(0, 100) }}...</p>
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" text @click="close" />
    </template>
  </Dialog>
</template>
```

#### 7.2 HistoryManagementPanel.vue
```vue
<template>
  <div class="history-panel">
    <div class="flex justify-content-between align-items-center mb-3">
      <h3>Conversation History</h3>
      <Button 
        icon="pi pi-plus" 
        size="small" 
        @click="createNewHistory"
        label="New Chat"
      />
    </div>

    <div class="histories-list">
      <div 
        v-for="history in histories" 
        :key="history.id"
        class="history-item cursor-pointer p-2 border-round hover:surface-100"
        :class="{ 'surface-100 border-left-2 border-blue-500': currentHistoryId === history.id }"
        @click="selectHistory(history.id)"
      >
        <div class="flex justify-content-between align-items-center">
          <span class="font-medium">{{ history.title }}</span>
          <span class="text-xs text-500">{{ history.message_count }} messages</span>
        </div>
        <div class="flex gap-2 mt-2">
          <Button 
            icon="pi pi-pencil" 
            size="small" 
            text 
            @click.stop="editHistory(history)"
          />
          <Button 
            icon="pi pi-trash" 
            size="small" 
            text 
            severity="danger"
            @click.stop="deleteHistory(history.id)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
```

## IMPLEMENTATION ORDER

1. **Update ChatRuntimeService.js** - New API methods
2. **Update Chat.vue** - New state management
3. **Update ChatHeader.vue** - Persona + history display
4. **Update ChatSessionBar.vue** - Persona navigation
5. **Update ChatMessages.vue** - History-based messages
6. **Update ChatMessageInput.vue** - History context
7. **Create new components** - PersonaSelection, HistoryManagement
8. **Test complete flow** - Persona → Session → History → Messages

## DATA FLOW

1. **Load personas** → Show in sidebar
2. **Select persona** → Show sessions for that persona
3. **Select session** → Show histories for that session
4. **Select history** → Load messages for that history
5. **Send message** → Message goes to current history
6. **Switch context** → Easy navigation between conversations

This gives you the simple, clean structure you want with proper state persistence!
