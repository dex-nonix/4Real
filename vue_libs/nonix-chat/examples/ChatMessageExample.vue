<!-- ChatMessageExample.vue -->
<!--
  Example component demonstrating the ChatMessageTypeManager system
  Shows how different message types are rendered dynamically
  Updated to use ChatMessageContainer instead of ChatMessages
-->
<script setup>
import { ref } from 'vue';
import ChatMessageContainer from '../components/ChatMessageContainer.vue';

const currentUserId = ref('user123');
const sessionId = ref('example-session');

// Example messages with different types
const messages = ref([
  {
    id: '1',
    message_type: 'text',
    sender_id: 'user123',
    content: 'Hello! This is a regular text message.',
    timestamp: '2024-01-01T10:00:00Z',
    status: 'delivered'
  },
  {
    id: '2',
    message_type: 'system',
    sender_id: 'system',
    content: 'User joined the chat',
    timestamp: '2024-01-01T10:01:00Z'
  },
  {
    id: '3',
    message_type: 'tool',
    sender_id: 'assistant',
    content: 'Executing search query...',
    timestamp: '2024-01-01T10:02:00Z',
    metadata: {
      toolName: 'Search Tool',
      toolParams: { query: 'example search', limit: 10 },
      executionStatus: 'success',
      result: 'Found 5 results matching your query'
    }
  },
  {
    id: '4',
    message_type: 'user',
    sender_id: 'user456',
    content: 'This is a user message from another user',
    timestamp: '2024-01-01T10:03:00Z',
    metadata: {
      userName: 'John Doe',
      userAvatar: null,
      isValid: true
    }
  },
  {
    id: '5',
    message_type: 'text',
    sender_id: 'user123',
    content: 'This is my own message',
    timestamp: '2024-01-01T10:04:00Z',
    status: 'sent'
  }
]);

// Mock session object for the example
const mockSession = ref({
  id: sessionId.value,
  session_name: 'Example Chat Session',
  persona: {
    name: 'Example Persona',
    description: 'A demo persona for testing'
  }
});

// Add new message function for testing
const addMessage = (type, text) => {
  const newMessage = {
    id: Date.now().toString(),
    message_type: type,
    sender_id: type === 'system' ? 'system' : 'user123',
    content: text,
    timestamp: new Date().toISOString(),
    status: 'sent',
    metadata: type === 'tool' ? {
      toolName: 'Test Tool',
      toolParams: { test: true },
      executionStatus: 'pending'
    } : type === 'user' ? {
      userName: 'Test User',
      userAvatar: null,
      isValid: true
    } : {}
  };
  
  messages.value.push(newMessage);
};

// Handle send message event
const handleSendMessage = (messageData) => {
  console.log('Message sent:', messageData);
  // In a real app, this would send to the backend
  addMessage('text', messageData.text);
};
</script>

<template>
  <div class="p-4">
    <h2 class="mb-4">ChatMessageTypeManager Demo</h2>
    
    <!-- Control Panel -->
    <div class="surface-100 p-3 border-round mb-4">
      <h3 class="mt-0 mb-3">Add Test Messages</h3>
      <div class="flex gap-2 flex-wrap">
        <button @click="addMessage('text', 'New text message')" class="p-button p-button-sm">
          Add Text
        </button>
        <button @click="addMessage('system', 'System notification')" class="p-button p-button-sm p-button-secondary">
          Add System
        </button>
        <button @click="addMessage('tool', 'Tool execution')" class="p-button p-button-sm p-button-info">
          Add Tool
        </button>
        <button @click="addMessage('user', 'User message')" class="p-button p-button-sm p-button-success">
          Add User
        </button>
      </div>
    </div>
    
    <!-- Message Count Display -->
    <div class="surface-200 p-2 border-round mb-4">
      <strong>Total Messages:</strong> {{ messages.length }}
      <span class="ml-3">
        <strong>Types:</strong> 
        <span v-for="type in ['text', 'system', 'tool', 'user']" :key="type" class="ml-2">
          {{ type }}: {{ messages.filter(m => m.message_type === type).length }}
        </span>
      </span>
    </div>
    
    <!-- Chat Message Container -->
    <div class="surface-ground border-round" style="height: 500px; overflow: hidden;">
      <ChatMessageContainer 
        :session-id="sessionId"
        :current-user-id="currentUserId"
        :selected-session="mockSession"
        @send-message="handleSendMessage"
      />
    </div>
  </div>
</template>
