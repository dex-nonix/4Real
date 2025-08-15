<!-- Chat.vue -->
<script setup>
import { ref, computed } from 'vue';
import ChatHeader from './ChatHeader.vue';
import ChatSessionBar from './ChatSessionBar.vue';
import ChatMessages from './ChatMessages.vue';
import ChatMessageInput from './ChatMessageInput.vue';

const props = defineProps({
  sessions: { type: Array, required: true },
  messages: { type: Array, required: true },
  currentUserId: { type: [String, Number], required: true }
});

const emit = defineEmits(['sendMessage', 'sessionSelected', 'closeChat']);

const selectedSessionId = ref(props.sessions.length > 0 ? props.sessions[0].id : null);
const newMessage = ref('');

const activeSession = computed(() => {
  return props.sessions.find(s => s.id === selectedSessionId.value);
});

const activeUser = computed(() => activeSession.value?.user);

const handleSessionSelected = (sessionId) => {
  selectedSessionId.value = sessionId;
  emit('sessionSelected', sessionId);
};

const handleSendMessage = (messageText) => {
  emit('sendMessage', {
    sessionId: selectedSessionId.value,
    text: messageText,
  });
};
</script>

<template>
  <div class="flex flex-column overflow-hidden " style="width: 1024px; height: 768px; border: 1px solid var(--surface-border)">
    <ChatHeader :user="activeUser" @close-chat="emit('closeChat')" />

    <div class="flex flex-row flex-1" style="min-height: 0;">
      <ChatSessionBar
        :sessions="sessions"
        :selected-session-id="selectedSessionId"
        @session-selected="handleSessionSelected"
      />
      <div class="flex flex-column flex-1">
        <ChatMessages
          :messages="messages"
          :current-user-id="currentUserId"
        />
        <ChatMessageInput v-model="newMessage" @send-message="handleSendMessage" />
      </div>
    </div>
  </div>
</template>