<template>
  <div
      class="window-pane"
      :class="windowPaneClasses"
      :style="{ ...windowPaneStyles, ...dockedPaneSize }"
      ref="windowPane"
  >
    <div
        class="window-pane-header"
        :class="{ 'is-draggable': state.dockSide === 'floating' }"
        @mousedown="handleMouseDown"
        ref="windowHeader"
        v-if="state.dockSide === 'floating'"
    >
      <span>Chat Pane</span>
      <div>
        <Button @click.stop="closePane" icon="pi pi-times" rounded text size="small" aria-label="Close" style="width: 22px; height: 22px; padding: 0;" />
      </div>
    </div>
    <div class="window-pane-content">
      <Chat :menuItems="chatMenuItems"/>
    </div>
    <div
        class="resize-handle"
        :class="`resize-${state.dockSide}`"
        @mousedown="handleResizeMouseDown"
        v-if="state.dockSide !== 'floating'"
    ></div>
  </div>
</template>

<script setup>
import {computed, onMounted, onUnmounted, reactive, ref, watch, nextTick} from 'vue';
import Chat from '@nonix-chat/components/Chat.vue';
import Button from 'primevue/button';

// --- STATE MANAGEMENT ---
const state = reactive({
  isVisible: false,
  isPinned: false,
  dockSide: 'right',
  floatingPos: {x: 50, y: 50},
  floatingSize: {width: 400, height: 500},
  dockedSize: 350,
});

// --- LOCALSTORAGE PERSISTENCE ---
const STORAGE_KEY = 'nonix-chat-pane-state-v1';

// Debounce utility for localStorage writes
let saveTimeout = null;
const debounceSave = (fn, delay = 300) => {
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(fn, delay);
};

// Save state to localStorage
const saveChatPaneState = () => {
  if (typeof window === 'undefined') return;

  try {
    const dataToSave = {
      isVisible: state.isVisible,
      isPinned: state.isPinned,
      dockSide: state.dockSide,
      floatingPos: { ...state.floatingPos },
      floatingSize: { ...state.floatingSize },
      dockedSize: state.dockedSize,
      timestamp: Date.now(),
      version: '1.0'
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
  } catch (error) {
    console.warn('Failed to save ChatPane state:', error);
  }
};

// Load state from localStorage
const loadChatPaneState = () => {
  if (typeof window === 'undefined') return null;

  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return null;

    const parsed = JSON.parse(saved);

    // Validate version and basic structure
    if (!parsed.version || typeof parsed.isVisible !== 'boolean') {
      return null;
    }

    return parsed;
  } catch (error) {
    console.warn('Failed to load ChatPane state:', error);
    return null;
  }
};

// Validate and clamp floating position to viewport
const validateFloatingPosition = (pos, size) => {
  if (typeof window === 'undefined') return pos;

  const maxX = Math.max(0, window.innerWidth - (size?.width || 400) - 20);
  const maxY = Math.max(0, window.innerHeight - (size?.height || 500) - 20);

  return {
    x: Math.max(0, Math.min(pos.x, maxX)),
    y: Math.max(0, Math.min(pos.y, maxY))
  };
};

// --- DOM ELEMENT REFS ---
const windowPane = ref(null);
const windowHeader = ref(null);

// --- COMPUTED PROPERTIES (for automatic class/style updates) ---

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

// Computed property for docked pane size
const dockedPaneSize = computed(() => {
  if (state.dockSide === 'floating') return {};

  if (state.dockSide === 'left' || state.dockSide === 'right') {
    return {width: `${state.dockedSize}px`};
  } else {
    return {height: `${state.dockedSize}px`};
  }
});

// Watch for state changes and save to localStorage (debounced)
watch(
  () => state,
  () => {
    debounceSave(saveChatPaneState);
  },
  { deep: true }
);

// --- METHODS ---

const toggleChatPane = () => state.isVisible = !state.isVisible;
const togglePin = () => state.isPinned = !state.isPinned;
const undockPane = () => state.dockSide = 'floating';
const closePane = () => { state.isVisible = false; }

// Menu items for Chat component - PIN and FLOAT toggles only
const chatMenuItems = ref([
  {
    label: 'Toggle Pin',
    icon: 'pi pi-lock',
    command: () => setTimeout(() => togglePin(), 0)
  },
  {
    label: 'Toggle Float',
    icon: 'pi pi-window-maximize',
    command: () => Promise.resolve().then(() => undockPane())
  }
]);

// Click outside logic to close the pane if it's not pinned
const handleClickOutside = (e) => {
  if (!state.isPinned && state.isVisible) {
    const clickedInsidePane = windowPane.value?.contains(e.target);

    // Check if clicked on any PrimeVue overlay - these are typically user-initiated
    // and shouldn't cause the pane to close
    const clickedOnOverlay = e.target.closest('.p-menu') !== null ||
                            e.target.closest('.p-menuitem-link') !== null ||
                            e.target.closest('.p-overlaypanel') !== null ||
                            e.target.closest('.p-dialog') !== null ||
                            e.target.closest('.p-dropdown-panel') !== null ||
                            e.target.closest('.p-multiselect-panel') !== null ||
                            e.target.closest('.p-overlay') !== null ||
                            e.target.closest('.p-tooltip') !== null ||
                            e.target.closest('.p-confirm-popup') !== null;

    if (!clickedInsidePane && !clickedOnOverlay) {
      state.isVisible = false;
    }
  }
};

// --- DRAG AND DOCK LOGIC ---
let dragOffset = {x: 0, y: 0};
let isResizing = false;
let resizeStartPos = {x: 0, y: 0};
let resizeStartSize = 0;

const handleMouseDown = (e) => {
  if (state.dockSide !== 'floating') return;
  e.preventDefault();

  const paneRect = windowPane.value.getBoundingClientRect();
  dragOffset.x = e.clientX - paneRect.left;
  dragOffset.y = e.clientY - paneRect.top;

  windowPane.value.classList.add('no-transition');
  document.querySelectorAll('.dock-zone').forEach(zone => zone.classList.add('active'));

  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp, {once: true});
};

const handleMouseMove = (e) => {
  if (isResizing) {
    let delta;
    if (state.dockSide === 'left' || state.dockSide === 'right') {
      delta = e.clientX - resizeStartPos.x;
      if (state.dockSide === 'right') {
        delta = -delta; // Invert for right side
      }
    } else {
      delta = e.clientY - resizeStartPos.y;
      if (state.dockSide === 'bottom') {
        delta = -delta; // Invert for bottom side
      }
    }

    state.dockedSize = Math.max(200, Math.min(800, resizeStartSize + delta));
  } else {
    state.floatingPos.x = e.clientX - dragOffset.x;
    state.floatingPos.y = e.clientY - dragOffset.y;
  }
};

const handleMouseUp = (e) => {
  windowPane.value.classList.remove('no-transition');
  document.querySelectorAll('.dock-zone').forEach(zone => zone.classList.remove('active'));
  document.removeEventListener('mousemove', handleMouseMove);

  if (isResizing) {
    isResizing = false;
    return;
  }

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

// Resize handle mouse down
const handleResizeMouseDown = (e) => {
  if (state.dockSide === 'floating') return;
  e.preventDefault();
  e.stopPropagation();

  isResizing = true;
  resizeStartPos.x = e.clientX;
  resizeStartPos.y = e.clientY;
  resizeStartSize = state.dockedSize;

  windowPane.value.classList.add('no-transition');
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp, {once: true});
};

// --- LIFECYCLE HOOKS ---
onMounted(async () => {
  // Load saved state from localStorage
  const savedState = loadChatPaneState();
  if (savedState) {
    try {
      // Validate and apply saved position if it's reasonable
      if (savedState.floatingPos && savedState.floatingSize) {
        const validatedPos = validateFloatingPosition(
          savedState.floatingPos,
          savedState.floatingSize
        );
        state.floatingPos = validatedPos;
      }

      // Apply other saved state properties
      state.isVisible = savedState.isVisible ?? false;
      state.isPinned = savedState.isPinned ?? false;
      state.dockSide = savedState.dockSide ?? 'right';
      state.floatingSize = savedState.floatingSize ?? { width: 400, height: 500 };
      state.dockedSize = savedState.dockedSize ?? 350;
    } catch (error) {
      console.warn('Failed to apply saved ChatPane state:', error);
    }
  }

  // Add global event listener for 'click outside'
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  // Clear any pending save timeout
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }

  // Clean up global event listener to prevent memory leaks
  document.removeEventListener('click', handleClickOutside);
  // Also remove mousemove in case it's still attached somehow
  document.removeEventListener('mousemove', handleMouseMove);
});

// Expose methods and state for parent component
defineExpose({
  state,
  toggleChatPane,
  togglePin,
  undockPane,
  closePane
});
</script>

<style>
/* --- Independent Window Pane --- */
.window-pane {
  position: fixed;
  background: #fff;
  z-index: 1000;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #ccc;
  border-radius: 4px;
  transition: all var(--transition-speed);
  opacity: 0;
  pointer-events: none;
}

.window-pane.no-transition {
  transition: none;
}

/* Used during drag for responsiveness */
.window-pane.is-visible {
  opacity: 1;
  pointer-events: auto;
}

.window-pane-header {
  padding: 8px 12px;
  background: #f1f1f1;
  border-bottom: 1px solid #ccc;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.window-pane-header.is-draggable {
  cursor: move;
}

.window-pane-content {
  flex-grow: 1;
  padding: 0rem;
  overflow-y: auto;
  min-height: 0; /* Allow flex item to shrink below its content size */
}

.window-pane.is-docked {
  border-radius: 0;
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.2);
}

.window-pane.docked-right {
  top: 0;
  right: 0;
  height: 100vh;
  height: 100dvh; /* Use dynamic viewport height for mobile browsers */
  border-width: 0 0 0 1px;
}

.window-pane.docked-left {
  top: 0;
  left: 0;
  height: 100vh;
  height: 100dvh; /* Use dynamic viewport height for mobile browsers */
  border-width: 0 1px 0 0;
}

.window-pane.docked-top {
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  height: 100dvh; /* Use dynamic viewport height for mobile browsers */
  border-width: 0 0 1px 0;
}

.window-pane.docked-bottom {
  bottom: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  height: 100dvh; /* Use dynamic viewport height for mobile browsers */
  border-width: 1px 0 0 0;
}

.window-pane.is-pinned {
  box-shadow: none !important;
}

/* Resize Handle */
.resize-handle {
  position: absolute;
  background: transparent;
  z-index: 1001;
}

.resize-left {
  top: 0;
  right: -3px;
  width: 6px;
  height: 100%;
  cursor: ew-resize;
}

.resize-right {
  top: 0;
  left: -3px;
  width: 6px;
  height: 100%;
  cursor: ew-resize;
}

.resize-top {
  bottom: -3px;
  left: 0;
  width: 100%;
  height: 6px;
  cursor: ns-resize;
}

.resize-bottom {
  top: -3px;
  left: 0;
  width: 100%;
  height: 6px;
  cursor: ns-resize;
}

.resize-handle:hover {
  background: rgba(0, 123, 255, 0.3);
}

/* Mobile-specific adjustments */
@media (max-width: 768px) {
  /* Make resize handles easier to grab on mobile */
  .resize-left,
  .resize-right {
    width: 12px; /* Wider touch targets */
    right: -6px;
  }

  .resize-top,
  .resize-bottom {
    height: 12px; /* Taller touch targets */
    top: -6px;
  }

  .resize-left {
    right: -6px;
  }

  .resize-right {
    left: -6px;
  }

  .resize-top {
    bottom: -6px;
  }

  .resize-bottom {
    top: -6px;
  }
}
</style>