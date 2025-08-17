<!-- Chat.vue -->
<script setup>
import { ref, computed } from 'vue';
import ChatHeader from './ChatHeader.vue';
import ChatSessionBar from './ChatSessionBar.vue';
import ChatMessages from './ChatMessages.vue';
import ChatMessageInput from './ChatMessageInput.vue';

const props = defineProps({
  sessions: { type: Array, required: true, default: () => [] },
  currentSessionId: { type: [String, Number, null], required: false, default: null },
  currentHistoryId: { type: [String, Number, null], required: false, default: null },
  currentUserId: { type: [String, Number], required: false, default: 'user-self' },
  histories: { type: Array, required: false, default: () => [] },
  messages: { type: Array, required: false, default: () => [] }
});

const emit = defineEmits(['sessionSelected', 'historySelected', 'sendMessage', 'closeChat', 'addPersona', 'viewHistory']);

const newMessage = ref('');

// Computed values with null safety
const currentSession = computed(() => {
  if (!props.currentSessionId || !props.sessions.length) return null;
  return props.sessions.find(s => s.id === props.currentSessionId);
});

const currentHistory = computed(() => {
  if (!props.currentHistoryId || !props.histories.length) return null;
  return props.histories.find(h => h.id === props.currentHistoryId);
});

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
      :persona="currentSession?.persona" 
      :current-session="currentSession"
      :current-history="currentHistory"
      @close-chat="emit('closeChat')" 
      @view-history="emit('viewHistory')"
    />

    <div class="flex flex-row flex-1" style="min-height: 0;">
      <ChatSessionBar
        :sessions="sessions"
        :current-session-id="currentSessionId"
        @session-selected="handleSessionSelected"
        @add-session="handleAddPersona"
      />
      <div class="flex flex-column flex-1">
        <ChatMessages
          :messages="messages"
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