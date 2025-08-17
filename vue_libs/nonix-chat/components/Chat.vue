<!-- Chat.vue -->
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
  currentHistoryId: { type: [String, Number], required: true },
  currentUserId: { type: [String, Number], required: true }
});

const emit = defineEmits(['personaSelected', 'sessionSelected', 'historySelected', 'sendMessage', 'closeChat']);

const newMessage = ref('');

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
        <ChatMessageInput 
          v-model="newMessage" 
          :current-history-id="currentHistoryId"
          @send-message="handleSendMessage" 
        />
      </div>
    </div>
  </div>
</template>