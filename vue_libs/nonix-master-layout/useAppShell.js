import { reactive } from 'vue'

// Simple shared shell state for left/right sidebars
const shellState = reactive({
  leftOpen: false,      // mobile off-canvas visibility
  leftCollapsed: false, // desktop pinned collapse
  rightOpen: false,     // right sidebar visibility
  rightPinned: false    // right sidebar pinned state
})

export function useAppShell() {
  function toggleLeft() {
    if (typeof window !== 'undefined' && window.innerWidth >= 768) {
      shellState.leftCollapsed = !shellState.leftCollapsed
    } else {
      shellState.leftOpen = !shellState.leftOpen
    }
  }

  function toggleRight() {
    shellState.rightOpen = !shellState.rightOpen
  }

  function openLeft() {
    shellState.leftOpen = true
  }

  function closeLeft() {
    shellState.leftOpen = false
  }

  function openRight() {
    shellState.rightOpen = true
  }

  function closeRight() {
    shellState.rightOpen = false
  }

  function togglePin() {
    shellState.rightPinned = !shellState.rightPinned
    // When pinning, ensure sidebar is open
    if (shellState.rightPinned) {
      shellState.rightOpen = true
    }
  }

  return {
    state: shellState,
    toggleLeft,
    toggleRight,
    openLeft,
    closeLeft,
    openRight,
    closeRight,
    togglePin
  }
}


