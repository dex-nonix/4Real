<template>
  <!-- Resizable sidebar container -->
  <div class="resizable-sidebar-container" v-show="shouldShowSidebar">
    <!-- Draggable divider -->
    <div class="sidebar-divider"
         :class="{ dragging: isResizing }"
         @mousedown="startResize"
         @touchstart="startResize">
      <div class="divider-handle"></div>
    </div>

    <!-- Sidebar content -->
    <div class="custom-sidebar" :style="{ width: sidebarWidth + 'px' }">
      <Chat
        :menu-items="chatMenuItems"
        @menu-item-click="handleMenuItemClick"
      />
    </div>
  </div>
</template>

<style scoped>
/* Resizable sidebar container */
.resizable-sidebar-container {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  height: 100vh;
  z-index: 999;
  display: flex;
}

/* Draggable divider */
.sidebar-divider {
  width: 8px;
  background: transparent;
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.sidebar-divider:hover,
.sidebar-divider.dragging {
  background: var(--primary-color);
}

.divider-handle {
  width: 2px;
  height: 24px;
  background: var(--surface-border);
  border-radius: 1px;
  transition: background-color 0.2s ease;
}

.sidebar-divider:hover .divider-handle,
.sidebar-divider.dragging .divider-handle {
  background: white;
}

/* Sidebar content */
.custom-sidebar {
  background: var(--surface-card);
  border-left: 1px solid var(--surface-border);
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 300px;
  max-width: 800px;
  transition: width 0.1s ease;
}
</style>

<script setup>
import { computed, ref, watch } from 'vue'
import { useAppShell } from './useAppShell.js'
import Chat from '@nonix-chat/components/Chat.vue'

const { state, togglePin } = useAppShell()

// Resizable sidebar state
const sidebarWidth = ref(450)
const isResizing = ref(false)
const startX = ref(0)
const startWidth = ref(0)

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
    command: () => handleChatClose(true)
  }
])

watch(() => state.rightPinned, (isPinned) => {
  chatMenuItems.value[0] = {
    ...chatMenuItems.value[0],
    icon: isPinned ? 'pi pi-lock' : 'pi pi-unlock',
    label: isPinned ? 'Unpin Chat' : 'Pin Chat'
  }
})


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

// Visibility logic: show when open OR when pinned on desktop
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
    // Auto-close: don't force, so pin status is respected
    handleChatClose(false);
  }
}

// Handle menu item clicks from ChatHeader
const handleMenuItemClick = (item) => {
  console.log('Menu item clicked:', item.label);
  // The item's command is already executed in ChatHeader, just log here
}

// Resize functionality
const startResize = (event) => {
  isResizing.value = true
  startX.value = event.clientX || event.touches[0].clientX
  startWidth.value = sidebarWidth.value

  // Add event listeners
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('touchmove', handleResize)
  document.addEventListener('mouseup', stopResize)
  document.addEventListener('touchend', stopResize)

  // Prevent text selection during resize
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'col-resize'

  event.preventDefault()
}

const handleResize = (event) => {
  if (!isResizing.value) return

  const clientX = event.clientX || event.touches[0].clientX
  const deltaX = startX.value - clientX
  const newWidth = Math.max(300, Math.min(800, startWidth.value + deltaX))

  sidebarWidth.value = newWidth
}

const stopResize = () => {
  isResizing.value = false

  // Remove event listeners
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('touchmove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  document.removeEventListener('touchend', stopResize)

  // Restore normal cursor and selection
  document.body.style.userSelect = ''
  document.body.style.cursor = ''
}

// Handle chat close through external menu system
const handleChatClose = (force = false) => {
  console.log('Chat close through menu system - closing sidebar, force:', force);

  // If not forced and pinned, don't close (auto-close prevention)
  if (!force && state.rightPinned) {
    console.log('Close prevented - sidebar is pinned');
    return;
  }

  // Close the sidebar
  state.rightOpen = false;
}
</script>


