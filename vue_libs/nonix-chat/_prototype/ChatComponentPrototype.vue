<template>
  <div class="flex h-screen bg-white font-sans text-gray-800 antialiased">
    <!-- Sidebar -->
    <div class="w-[72px] border-r border-gray-200 flex flex-col items-center py-4 space-y-1 bg-white flex-shrink-0">
      <div 
        v-for="user in users" 
        :key="user.id"
        class="relative p-2"
        @click="selectUser(user.id)"
        >
        <button class="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 rounded-full">
          <Avatar :image="user.avatar" size="large" shape="circle" />
        </button>
        <div v-if="user.id === activeUserId" class="absolute left-0 top-1/2 -translate-y-1/2 h-8 w-1 bg-[#2DD4BF] rounded-r-full"></div>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col bg-[#F9FAFB]">
      <!-- Chat Header -->
      <div v-if="activeChatUser" class="flex items-center justify-between py-3 px-6 border-b border-gray-200 bg-white">
        <div class="flex items-center space-x-4">
          <Avatar :image="activeChatUser.avatar" size="large" shape="circle" />
          <span class="font-semibold text-lg text-gray-800">{{ activeChatUser.name }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <Button icon="pi pi-replay" class="p-button-rounded p-button-text text-gray-500 hover:bg-gray-100" />
          <Button icon="pi pi-times" class="p-button-rounded p-button-text text-gray-500 hover:bg-gray-100" />
        </div>
      </div>

      <!-- Chat Messages -->
      <div class="flex-1 p-6 space-y-6 overflow-y-auto">
        <div v-for="message in activeChatMessages" :key="message.id">
          <div :class="['flex', message.senderId === currentUserId ? 'justify-end' : 'justify-start']">
            <div class="max-w-lg">
              <div class="relative bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                <p class="text-gray-700">{{ message.text }}</p>
                <Button icon="pi pi-ellipsis-v" class="absolute top-2 right-2 p-button-rounded p-button-text p-button-sm text-gray-400" />
              </div>
              <div :class="['flex items-center mt-1.5', message.senderId === currentUserId ? 'justify-end' : 'justify-start']">
                <i v-if="message.senderId === currentUserId" :class="statusIcon(message.status)" class="text-gray-400 text-xs mr-1.5"></i>
                <span class="text-xs text-gray-400">{{ message.timestamp }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Message Input -->
      <div class="p-4 border-t border-gray-200 bg-white flex items-center space-x-4">
        <Button icon="pi pi-plus" class="p-button-rounded p-button-text text-gray-500 text-2xl" />
        <div class="flex-1 flex items-center bg-gray-100 rounded-lg px-4 py-2">
          <i class="pi pi-box text-gray-500"></i>
          <InputText 
            v-model="newMessage" 
            placeholder="Type a message..." 
            class="flex-1 bg-transparent border-0 focus:ring-0 text-gray-700 placeholder-gray-500 ml-3"
            @keydown.enter.prevent="sendMessage"
          />
          <Button icon="pi pi-replay" class="p-button-rounded p-button-text text-gray-500" />
          <Button icon="pi pi-send" class="p-button-rounded p-button-text text-gray-500" @click="sendMessage" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';

// --- TYPE DEFINITIONS ---
// interface User {
//   id: number;
//   name: string;
//   avatar: string;
// }
// type MessageStatus = 'pending' | 'sent' | 'delivered' | 'read';
// interface Message {
//   id: number;
//   text: string;
//   timestamp: string;
//   senderId: number;
//   status: MessageStatus;
// }

// --- STATE ---
const currentUserId = ref(1); // The ID of the user using the app
const activeUserId = ref(2); // The ID of the user being chatted with
const newMessage = ref('');

const users = reactive([
  { id: 2, name: 'Esther Howard', avatar: 'https://i.pravatar.cc/150?u=2' },
  { id: 3, name: 'Jane Cooper', avatar: 'https://i.pravatar.cc/150?u=3' },
  { id: 4, name: 'Cody Fisher', avatar: 'https://i.pravatar.cc/150?u=4' },
  { id: 5, name: 'Robert Fox', avatar: 'https://i.pravatar.cc/150?u=5' },
  { id: 6, name: 'Dianne Russell', avatar: 'https://i.pravatar.cc/150?u=6' },
  { id: 7, name: 'Wade Warren', avatar: 'https://i.pravatar.cc/150?u=7' },
  { id: 8, name: 'Cameron Williamson', avatar: 'https://i.pravatar.cc/150?u=8' },
]);

const messages = reactive({
  2: [ // Chat with Esther Howard (id: 2)
    { id: 1, senderId: 1, text: "Hey, I'm finalizing the UI for the launch—color scheme is set, but I'm tweaking typography for all devices. What do you think of the mockups?", timestamp: '14:43', status: 'delivered' },
    { id: 2, senderId: 2, text: "Looks great, but button hover effects are lagging on older browsers—I'll optimize them. Let me know if you want to adjust the animation timing. 😉", timestamp: '14:53', status: 'read' },
    { id: 3, senderId: 1, text: "The design is solid, and I've updated the backend for launch, but there's a minor form validation issue on the contact page I'm fixing now.", timestamp: '14:53', status: 'pending' },
  ],
  3: [],
  4: [],
  5: [],
  6: [],
  7: [],
  8: [],
});

// --- COMPUTED PROPERTIES ---
const activeChatUser = computed(() => users.find(user => user.id === activeUserId.value));
const activeChatMessages = computed(() => messages[activeUserId.value] || []);

// --- METHODS ---
const selectUser = (userId) => {
  activeUserId.value = userId;
};

const sendMessage = () => {
  if (newMessage.value.trim() === '') return;

  const newMsg = {
    id: Date.now(),
    senderId: currentUserId.value,
    text: newMessage.value,
    timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
    status: 'pending',
  };

  if (!messages[activeUserId.value]) {
    messages[activeUserId.value] = [];
  }
  messages[activeUserId.value].push(newMsg);
  newMessage.value = '';

  // Simulate message being sent and delivered
  setTimeout(() => {
    const sentMessage = messages[activeUserId.value].find(m => m.id === newMsg.id);
    if (sentMessage) {
      sentMessage.status = 'delivered';
    }
  }, 1500);
};

const statusIcon = (status) => {
  switch (status) {
    case 'pending':
      return 'pi pi-clock';
    case 'delivered':
    case 'sent':
    case 'read':
      return 'pi pi-check';
    default:
      return '';
  }
};
</script>