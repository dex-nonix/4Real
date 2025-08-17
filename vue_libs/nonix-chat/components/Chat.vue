<!-- Chat.vue -->
<script setup>
import { ref, computed } from 'vue';
import ChatHeader from './ChatHeader.vue';
import ChatSessionBar from './ChatSessionBar.vue';
import ChatMessages from './ChatMessages.vue';
import ChatMessageInput from './ChatMessageInput.vue';

const props = defineProps({
  personas: { type: Array, required: true, default: () => [] },
  currentPersonaId: { type: [String, Number, null], required: false, default: null },
  currentSessionId: { type: [String, Number, null], required: false, default: null },
  currentHistoryId: { type: [String, Number, null], required: false, default: null },
  currentUserId: { type: [String, Number], required: false, default: 'user-self' }
});

const emit = defineEmits(['personaSelected', 'sessionSelected', 'historySelected', 'sendMessage', 'closeChat', 'addPersona']);

const newMessage = ref('');

// Computed values with null safety
const currentPersona = computed(() => {
  if (!props.currentPersonaId || !props.personas.length) return null;
  return props.personas.find(p => p.id === props.currentPersonaId);
});

const currentSession = computed(() => {
  if (!currentPersona.value || !props.currentSessionId) return null;
  return currentPersona.value.sessions?.find(s => s.id === props.currentSessionId);
});

const currentHistory = computed(() => {
  if (!currentSession.value || !props.currentHistoryId) return null;
  return currentSession.value.histories?.find(h => h.id === props.currentHistoryId);
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
  if (!props.currentHistoryId) return;
  emit('sendMessage', {
    historyId: props.currentHistoryId,
    text: messageText,
  });
};

const handleAddPersona = () => {
  emit('addPersona');
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
        @addPersona="handleAddPersona"
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