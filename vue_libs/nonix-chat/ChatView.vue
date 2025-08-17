<template>
  <div class="chat-view surface-card p-3 border-round">
    <!-- Simple page wrapper that uses Chat component -->
    <Chat />
  </div>
</template>

<script setup>
import Chat from './components/Chat.vue'

// ChatView is a PAGE/VIEW component - no props, no state, no events
// It's just a simple wrapper around the Chat component
// Used once per route, handles routing and page-level concerns only
</script>

<style scoped>
.chat-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
