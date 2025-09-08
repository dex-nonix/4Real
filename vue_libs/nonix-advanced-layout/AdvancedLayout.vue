<template>
  <div class="app-container" :class="appContainerClasses" ref="appContainer">
    <!-- Docking Zones -->
    <div class="dock-zone" id="dock-zone-top" data-dock="top"></div>
    <div class="dock-zone" id="dock-zone-right" data-dock="right"></div>
    <div class="dock-zone" id="dock-zone-bottom" data-dock="bottom"></div>
    <div class="dock-zone" id="dock-zone-left" data-dock="left"></div>

    <div class="layout-wrapper">
      <div class="the-top-bar" :class="{ collapsed: isTopBarCollapsed }">
        <button @click="toggleNav">Toggle Nav</button>
        <button @click="toggleFooter">Toggle Footer</button>
        <button @click.stop="toggleChatPane" style="float: right;" ref="toggleChatBtn">Toggle Chat</button>
      </div>
      <div class="the-main-area">
        <div class="left-navigation" :class="{ collapsed: isNavCollapsed }">
          <h3>Navigation</h3>
        </div>
        <div class="the-content-area">
          <h1>Main Content</h1>
          <p><b>Bug Fixes Implemented (in Vue):</b><br>1. The "click outside to close" feature now works correctly for both floating and docked (but unpinned) states.<br>2. The floating window no longer jumps when you start dragging it.</p>
        </div>
      </div>
      <div class="footer" :class="{ collapsed: isFooterCollapsed }">Toggleable Footer</div>
    </div>

    <div
      class="window-pane"
      :class="windowPaneClasses"
      :style="windowPaneStyles"
      ref="windowPane"
    >
      <div
        class="window-pane-header"
        :class="{ 'is-draggable': state.dockSide === 'floating' }"
        @mousedown="handleMouseDown"
        ref="windowHeader"
      >
        <span>Chat Pane</span>
        <div>
          <button @click.stop="togglePin" :disabled="state.dockSide === 'floating'">
            {{ state.isPinned ? 'Unpin' : 'Pin' }}
          </button>
          <button @click.stop="undockPane" :disabled="state.dockSide === 'floating'">Float</button>
        </div>
      </div>
      <div class="window-pane-content">Pane Content</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';

// --- STATE MANAGEMENT ---
const state = reactive({
  isVisible: false,
  isPinned: false,
  dockSide: 'right', // 'right', 'left', 'top', 'bottom', or 'floating'
  floatingPos: { x: 50, y: 50 },
  floatingSize: { width: 400, height: 500 },
});

// UI Element Collapse States
const isNavCollapsed = ref(false);
const isFooterCollapsed = ref(false);
const isTopBarCollapsed = ref(false); // Can be used if needed

// --- DOM ELEMENT REFS ---
const appContainer = ref(null);
const windowPane = ref(null);
const windowHeader = ref(null);
const toggleChatBtn = ref(null);

// --- COMPUTED PROPERTIES (for automatic class/style updates) ---

// Determines if the main layout should be pushed by the pane
const isLayoutPushed = computed(() => state.isPinned && state.isVisible && state.dockSide !== 'floating');

// Dynamically computes classes for the main app container
const appContainerClasses = computed(() => ({
  'pane-is-pinned-and-visible': isLayoutPushed.value,
  [`pushed-from-${state.dockSide}`]: isLayoutPushed.value,
}));

// Dynamically computes classes for the window pane
const windowPaneClasses = computed(() => ({
  'is-visible': state.isVisible,
  'is-pinned': state.isPinned,
  'is-docked': state.dockSide !== 'floating',
  [`docked-${state.dockSide}`]: state.dockSide !== 'floating',
  'is-floating': state.dockSide === 'floating',
}));

// Dynamically computes inline styles for the window pane (only when floating)
const windowPaneStyles = computed(() => {
  if (state.dockSide === 'floating') {
    return {
      left: `${state.floatingPos.x}px`,
      top: `${state.floatingPos.y}px`,
      width: `${state.floatingSize.width}px`,
      height: `${state.floatingSize.height}px`,
    };
  }
  return {};
});


// --- METHODS ---

const toggleNav = () => isNavCollapsed.value = !isNavCollapsed.value;
const toggleFooter = () => isFooterCollapsed.value = !isFooterCollapsed.value;
const toggleChatPane = () => state.isVisible = !state.isVisible;
const togglePin = () => state.isPinned = !state.isPinned;
const undockPane = () => state.dockSide = 'floating';

// Click outside logic to close the pane if it's not pinned
const handleClickOutside = (e) => {
  if (!state.isPinned && state.isVisible) {
    const clickedInsidePane = windowPane.value?.contains(e.target);
    const clickedOnOpenButton = toggleChatBtn.value?.contains(e.target);
    if (!clickedInsidePane && !clickedOnOpenButton) {
      state.isVisible = false;
    }
  }
};


// --- DRAG AND DOCK LOGIC ---
let dragOffset = { x: 0, y: 0 };

const handleMouseDown = (e) => {
  if (state.dockSide !== 'floating') return;
  e.preventDefault();

  const paneRect = windowPane.value.getBoundingClientRect();
  dragOffset.x = e.clientX - paneRect.left;
  dragOffset.y = e.clientY - paneRect.top;

  windowPane.value.classList.add('no-transition');
  document.querySelectorAll('.dock-zone').forEach(zone => zone.classList.add('active'));

  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp, { once: true });
};

const handleMouseMove = (e) => {
  state.floatingPos.x = e.clientX - dragOffset.x;
  state.floatingPos.y = e.clientY - dragOffset.y;
};

const handleMouseUp = (e) => {
  windowPane.value.classList.remove('no-transition');
  document.querySelectorAll('.dock-zone').forEach(zone => zone.classList.remove('active'));
  document.removeEventListener('mousemove', handleMouseMove);

  let didDock = false;
  const dockZones = document.querySelectorAll('.dock-zone');
  for (const zone of dockZones) {
    const zoneRect = zone.getBoundingClientRect();
    if (e.clientX > zoneRect.left && e.clientX < zoneRect.right && e.clientY > zoneRect.top && e.clientY < zoneRect.bottom) {
      state.dockSide = zone.dataset.dock;
      state.isPinned = false; // Un-pin by default on dock for consistent UX
      didDock = true;
      break;
    }
  }
};


// --- LIFECYCLE HOOKS ---
onMounted(() => {
  // Add global event listener for 'click outside'
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  // Clean up global event listener to prevent memory leaks
  document.removeEventListener('click', handleClickOutside);
  // Also remove mousemove in case it's still attached somehow
  document.removeEventListener('mousemove', handleMouseMove);
});

</script>

<style>
/*
  The original CSS is used directly as it is self-contained.
  The 'scoped' attribute is omitted to allow the 'body' style to apply globally,
  mimicking the behavior of the original HTML file.
*/
:root {
  --side-pane-dimension: 350px; /* Used for width when vertical, height when horizontal */
  --left-nav-width: 200px;
  --transition-speed: 0.25s ease-out;
}

/* Basic Setup - Applied to the host page if this component is the root */
body {
  margin: 0;
  font-family: sans-serif;
  background-color: #f4f4f4;
  overflow: hidden;
}

/* --- Master Container & Layout --- */
.app-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
.layout-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: margin var(--transition-speed);
}

/* PUSH LOGIC */
.app-container.pane-is-pinned-and-visible.pushed-from-left .layout-wrapper { margin-left: var(--side-pane-dimension); }
.app-container.pane-is-pinned-and-visible.pushed-from-right .layout-wrapper { margin-right: var(--side-pane-dimension); }
.app-container.pane-is-pinned-and-visible.pushed-from-top .layout-wrapper { margin-top: var(--side-pane-dimension); }
.app-container.pane-is-pinned-and-visible.pushed-from-bottom .layout-wrapper { margin-bottom: var(--side-pane-dimension); }

/* Component Styles */
.the-top-bar {
  padding: 1rem;
  background: #fff;
  border-bottom: 1px solid #ccc;
  flex-shrink: 0;
  z-index: 10;
  transition: all var(--transition-speed);
  overflow: hidden;
}
.the-top-bar.collapsed {
  height: 0;
  padding-top: 0;
  padding-bottom: 0;
  border-width: 0;
}
.the-main-area {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
}
.the-content-area {
  flex-grow: 1;
  padding: 1.5rem;
  overflow-y: auto;
}
.left-navigation {
  width: var(--left-nav-width);
  background: #f8f8f8;
  border-right: 1px solid #ccc;
  padding: 1rem;
  overflow-y: auto;
  flex-shrink: 0;
  transition: width var(--transition-speed), padding var(--transition-speed);
}
.left-navigation.collapsed {
  width: 0;
  padding: 0;
}
.footer {
  padding: 1rem;
  background: #fff;
  border-top: 1px solid #ccc;
  text-align: center;
  flex-shrink: 0;
  transition: all var(--transition-speed);
  overflow: hidden;
}
.footer.collapsed {
  height: 0;
  padding-top: 0;
  padding-bottom: 0;
  border-width: 0;
}

/* --- Independent Window Pane --- */
.window-pane {
  position: fixed;
  background: #fff;
  z-index: 1000;
  box-shadow: 0 5px 20px rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #ccc;
  border-radius: 4px;
  transition: all var(--transition-speed);
  opacity: 0;
  pointer-events: none;
}
.window-pane.no-transition { transition: none; } /* Used during drag for responsiveness */
.window-pane.is-visible { opacity: 1; pointer-events: auto; }
.window-pane-header {
  padding: 8px 12px;
  background: #f1f1f1;
  border-bottom: 1px solid #ccc;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.window-pane-header.is-draggable { cursor: move; }
.window-pane-content {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
}
.window-pane.is-docked { border-radius: 0; box-shadow: -5px 0 15px rgba(0,0,0,0.2); }
.window-pane.docked-right { top: 0; right: 0; width: var(--side-pane-dimension); height: 100vh; border-width: 0 0 0 1px; }
.window-pane.docked-left { top: 0; left: 0; width: var(--side-pane-dimension); height: 100vh; border-width: 0 1px 0 0; }
.window-pane.docked-top { top: 0; left: 0; width: 100vw; height: var(--side-pane-dimension); border-width: 0 0 1px 0; }
.window-pane.docked-bottom { bottom: 0; left: 0; width: 100vw; height: var(--side-pane-dimension); border-width: 1px 0 0 0; }
.window-pane.is-pinned { box-shadow: none !important; }

/* --- Docking Drop Zones --- */
.dock-zone {
  position: fixed;
  background: rgba(0, 123, 255, 0.2);
  border: 1px dashed #007bff;
  z-index: 9998;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}
.dock-zone.active { opacity: 1; }
#dock-zone-top { top: 0; left: 0; right: 0; height: 15%; }
#dock-zone-right { top: 0; right: 0; bottom: 0; width: 15%; }
#dock-zone-bottom { bottom: 0; left: 0; right: 0; height: 15%; }
#dock-zone-left { top: 0; left: 0; bottom: 0; width: 15%; }
</style>