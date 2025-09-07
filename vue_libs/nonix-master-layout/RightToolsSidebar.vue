<template>
  <!-- Overlay always present, just hidden/shown with CSS -->
  <div class="custom-sidebar-overlay" :class="{ 'overlay-visible': shouldShowSidebar }" @click="handleOverlayClick">
    <div class="custom-sidebar">
      <Chat
        :menu-items="chatMenuItems"
        @menu-item-click="handleMenuItemClick"
      />
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
import { computed, ref, watch } from 'vue'
import { useAppShell } from './useAppShell.js'
import Chat from '@nonix-chat/components/Chat.vue'

const { state, togglePin } = useAppShell()

// Menu items for ChatHeader - defined externally and reactive
const chatMenuItems = ref([
  {
    label: 'Pin Chat',
    icon: state.rightPinned ? 'pi pi-lock' : 'pi pi-unlock',
    command: () => togglePin()
  },
  {
    label: 'Close Chat',
    icon: 'pi pi-times',
    command: () => handleChatClose()
  }
])

// Update pin icon when pin state changes
watch(() => state.rightPinned, (isPinned) => {
  chatMenuItems.value[0].icon = isPinned ? 'pi pi-lock' : 'pi pi-unlock'
  chatMenuItems.value[0].label = isPinned ? 'Unpin Chat' : 'Pin Chat'
})

// Set initial icon state
chatMenuItems.value[0].icon = state.rightPinned ? 'pi pi-lock' : 'pi pi-unlock'
chatMenuItems.value[0].label = state.rightPinned ? 'Unpin Chat' : 'Pin Chat'

// Mobile detection for pin behavior
const isMobile = ref(false)
const updateMobileState = () => {
  isMobile.value = window.innerWidth < 768
}

// Handle window resize
if (typeof window !== 'undefined') {
  updateMobileState()
  window.addEventListener('resize', updateMobileState)
}

// Visibility logic: pinned on desktop = always visible, mobile = overlay
const shouldShowSidebar = computed(() => {
  if (state.rightPinned && !isMobile.value) {
    return true // Desktop pinned = always visible
  }
  return state.rightOpen // Mobile or unpinned = normal toggle
})

// Handle overlay click (dismiss sidebar)
const handleOverlayClick = (event) => {
  // Only close if clicked on the overlay itself, not on the sidebar content
  if (event.target === event.currentTarget) {
    // Don't close if pinned on desktop
    if (!(state.rightPinned && !isMobile.value)) {
      state.rightOpen = false;
    }
  }
}

// Handle menu item clicks from ChatHeader
const handleMenuItemClick = (item) => {
  console.log('Menu item clicked:', item.label);
  // The item's command is already executed in ChatHeader, just log here
}

// Handle chat close through external menu system
const handleChatClose = () => {
  console.log('Chat close through menu system - closing sidebar');
  state.rightOpen = false;
}
</script>


