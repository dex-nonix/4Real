<!-- ChatExample.vue -->
<script setup>
import { ref } from 'vue';
import Chat from './Chat.vue';

const CURRENT_USER_ID = 'user-self';

// --- DUMMY DATA ---
const sessions = ref([
  { id: 1, user: { name: 'Esther Howard', avatarUrl: 'https://randomuser.me/api/portraits/women/44.jpg' } },
  { id: 2, user: { name: 'Jane Cooper', avatarUrl: 'https://randomuser.me/api/portraits/women/68.jpg' } },
  { id: 3, user: { name: 'Cody Fisher', avatarUrl: 'https://randomuser.me/api/portraits/men/32.jpg' } },
  { id: 4, user: { name: 'Kristin Watson', avatarUrl: 'https://randomuser.me/api/portraits/women/17.jpg' } },
]);

const allMessages = {
  1: [
    { id: 101, text: "Hey, I'm finalizing the UI for the launch—color scheme is set, but I'm tweaking typography for all devices. What do you think of the mockups?", senderId: CURRENT_USER_ID, timestamp: '14:43', status: 'delivered' },
    { id: 102, text: "Looks great, but button hover effects are lagging on older browsers—I'll optimize them. Let me know if you want to adjust the animation timing. 😉", senderId: 'user-esther', timestamp: '14:53', status: 'sent' },
    { id: 103, text: "The design is solid, and I've updated the backend for launch, but there's a minor form validation issue on the contact page I'm fixing now.", senderId: CURRENT_USER_ID, timestamp: '14:53', status: 'pending' },
  ],
  2: [ { id: 201, text: "Hi Jane, do you have the latest report?", senderId: CURRENT_USER_ID, timestamp: '11:20', status: 'sent' } ],
  3: [ { id: 301, text: "Let's catch up later today.", senderId: 'user-cody', timestamp: '09:05', status: 'sent' } ],
};

const activeMessages = ref(allMessages[1]);

// --- EVENT HANDLERS ---
const onSessionSelected = (sessionId) => {
  activeMessages.value = allMessages[sessionId] || [];
};

const onSendMessage = ({ sessionId, text }) => {
  const newMessage = {
    id: Date.now(),
    text: text,
    senderId: CURRENT_USER_ID,
    timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
    status: 'pending',
  };
  if (!allMessages[sessionId]) allMessages[sessionId] = [];
  allMessages[sessionId].push(newMessage);
  activeMessages.value = [...allMessages[sessionId]];
};

const onCloseChat = () => {
  alert('Close chat clicked!');
};
</script>

<template>
  <div class="surface-ground flex align-items-center justify-content-center min-h-screen p-4">
    <Chat
      :sessions="sessions"
      :messages="activeMessages"
      :current-user-id="CURRENT_USER_ID"
      @session-selected="onSessionSelected"
      @send-message="onSendMessage"
      @close-chat="onCloseChat"
    />
  </div>
</template>