<template>
  <!-- Overlay always present, just hidden/shown with CSS -->
  <div class="custom-sidebar-overlay" :class="{ 'overlay-visible': visible }" @click="handleOverlayClick">
    <div class="custom-sidebar">
      <Chat @close-chat="handleChatClose" />
    </div>
  </div>
</template>

<style scoped>
.custom-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
}

.custom-sidebar-overlay.overlay-visible {
  opacity: 1;
  visibility: visible;
}

.custom-sidebar {
  width: 450px;
  background: var(--surface-card);
  border-left: 1px solid var(--surface-border);
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform: translateX(100%);
  transition: transform 0.3s ease;
}

.overlay-visible .custom-sidebar {
  transform: translateX(0);
}
</style>

<script setup>
import { computed } from 'vue'
import { useAppShell } from './useAppShell.js'
import Chat from '@nonix-chat/components/Chat.vue'

const { state } = useAppShell()
const visible = computed({
  get: () => state.rightOpen,
  set: (v) => { state.rightOpen = v }
})

// Handle overlay click (dismiss sidebar)
const handleOverlayClick = (event) => {
  // Only close if clicked on the overlay itself, not on the sidebar content
  if (event.target === event.currentTarget) {
    state.rightOpen = false;
  }
}

// Handle chat close event from Chat component
const handleChatClose = () => {
  console.log('Chat close event received - closing sidebar');
  state.rightOpen = false;
}
</script>


