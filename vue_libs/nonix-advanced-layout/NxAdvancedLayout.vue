<template>
  <div class="app-container" :class="appContainerClasses" ref="appContainer">
    <!-- Docking Zones -->
    <div class="dock-zone" id="dock-zone-top" data-dock="top"></div>
    <div class="dock-zone" id="dock-zone-right" data-dock="right"></div>
    <div class="dock-zone" id="dock-zone-bottom" data-dock="bottom"></div>
    <div class="dock-zone" id="dock-zone-left" data-dock="left"></div>

    <div class="layout-wrapper">
      <AdvancedTopBar
        :collapsed="isTopBarCollapsed"
        :title="layoutState.header.title"
        :actions="layoutState.header.actions"
        @toggle-nav="toggleNav"
        @toggle-chat="toggleChatPane"
      />
      <div class="the-main-area">
        <div class="left-navigation" :class="{ collapsed: isNavCollapsed }">
          <LeftNavSidebar />
        </div>
        <div class="the-content-area">
          <slot/>
        </div>
      </div>
      <div class="footer" :class="{ collapsed: isFooterCollapsed }">Toggleable Footer</div>
    </div>

    <ChatPane ref="chatPaneRef" />
  </div>
</template>

<script setup>
import {computed, ref} from 'vue';
import LeftNavSidebar from "@nonix-advanced-layout/LeftNavSidebar.vue";
import AdvancedTopBar from "@nonix-advanced-layout/AdvancedTopBar.vue";
import ChatPane from "@nonix-advanced-layout/ChatPane.vue";
import { useNxAdvancedLayout } from './useNxAdvancedLayout.js';


// UI Element Collapse States
const isNavCollapsed = computed({
  get: () => layoutState.leftCollapsed,
  set: (value) => layoutState.leftCollapsed = value
});
const isFooterCollapsed = ref(false);
const isTopBarCollapsed = ref(false); // Can be used if needed

// Advanced Layout Composable
const { state: layoutState } = useNxAdvancedLayout();

// --- DOM ELEMENT REFS ---
const appContainer = ref(null);
const chatPaneRef = ref(null);

// --- COMPUTED PROPERTIES (for automatic class/style updates) ---

// Determines if the main layout should be pushed by the pane
const isLayoutPushed = computed(() => {
  const paneState = chatPaneRef.value?.state;
  return paneState?.isPinned && paneState?.isVisible && paneState?.dockSide !== 'floating';
});

// Dynamically computes classes for the main app container
const appContainerClasses = computed(() => {
  const paneState = chatPaneRef.value?.state;
  return {
    'pane-is-pinned-and-visible': isLayoutPushed.value,
    [`pushed-from-${paneState?.dockSide}`]: isLayoutPushed.value,
  };
});


// Computed property for CSS v-bind (returns pixel value as string)
const dockedSizePx = computed(() => {
  const paneState = chatPaneRef.value?.state;
  return paneState?.dockedSize ? `${paneState.dockedSize}px` : '0px';
});

// --- METHODS ---

const toggleNav = () => isNavCollapsed.value = !isNavCollapsed.value;
const toggleFooter = () => isFooterCollapsed.value = !isFooterCollapsed.value;
const toggleChatPane = () => chatPaneRef.value?.toggleChatPane();
const toggleRightSidebar = () => layoutState.rightOpen = !layoutState.rightOpen;








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
  overflow: auto; /* Allow natural scrolling on mobile */
  min-height: 100vh;
  min-height: 100dvh; /* Use dynamic viewport height for mobile browsers */
}

/* --- Master Container & Layout --- */
.app-container {
  position: relative;
  width: 100vw;
  min-height: 100vh;
  min-height: 100dvh; /* Use dynamic viewport height for mobile browsers */
  overflow: visible; /* Allow content to flow naturally */
}

.layout-wrapper {
  min-height: 100vh;
  min-height: 100dvh; /* Use dynamic viewport height for mobile browsers */
  display: flex;
  flex-direction: column;
  transition: margin var(--transition-speed);
}

/* PUSH LOGIC - Now uses dynamic sizing */
.app-container.pane-is-pinned-and-visible.pushed-from-left .layout-wrapper {
  margin-left: v-bind('dockedSizePx');
}

.app-container.pane-is-pinned-and-visible.pushed-from-right .layout-wrapper {
  margin-right: v-bind('dockedSizePx');
}

.app-container.pane-is-pinned-and-visible.pushed-from-top .layout-wrapper {
  margin-top: v-bind('dockedSizePx');
}

.app-container.pane-is-pinned-and-visible.pushed-from-bottom .layout-wrapper {
  margin-bottom: v-bind('dockedSizePx');
}

/* RESET MARGINS WHEN PANE IS NOT ACTIVE */
.app-container:not(.pane-is-pinned-and-visible) .layout-wrapper {
  margin: 0 !important;
}

.app-container:not(.pane-is-pinned-and-visible).pushed-from-left .layout-wrapper {
  margin-left: 0 !important;
}

.app-container:not(.pane-is-pinned-and-visible).pushed-from-right .layout-wrapper {
  margin-right: 0 !important;
}

.app-container:not(.pane-is-pinned-and-visible).pushed-from-top .layout-wrapper {
  margin-top: 0 !important;
}

.app-container:not(.pane-is-pinned-and-visible).pushed-from-bottom .layout-wrapper {
  margin-bottom: 0 !important;
}

/* Component Styles */
.the-top-bar {
  padding: 1rem;
  background: #fff;
  border-bottom: 1px solid #ccc;
  flex-shrink: 0;
  z-index: 10;
  transition: all var(--transition-speed);
  overflow: visible;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 44px;
  position: relative;
}

.the-top-bar.collapsed {
  height: 0;
  padding-top: 0;
  padding-bottom: 0;
  border-width: 0;
}

.the-top-bar > button:last-of-type {
  margin-left: auto;
  float: none !important;
}

.the-main-area {
  display: flex;
  flex-grow: 1;
  overflow: visible; /* Allow content to scroll naturally */
  min-height: 0; /* Allow flex item to shrink below its content size */
}

.the-content-area {
  flex-grow: 1;
  padding: 1.5rem;
  overflow-y: auto;
  min-height: 0; /* Allow flex item to shrink below its content size */
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
  overflow: visible; /* Allow footer content to be visible */
  position: relative; /* Ensure footer stays in normal flow */
  z-index: 5; /* Keep footer below interactive elements but above content */
}

.footer.collapsed {
  display: none !important; /* Completely remove from layout */
}

@media (max-width: 768px) {
  .the-top-bar {
    padding: 0.75rem;
    min-height: 48px;
  }

  .the-content-area {
    padding: 1rem;
  }

  .left-navigation {
    width: var(--left-nav-width);
    padding: 0.75rem;
  }

  .footer {
    padding: 0.75rem;
    font-size: 0.9rem;
  }
}

/* Ensure footer visibility on all devices */
@media (max-height: 600px) {
  .footer {
    padding: 0.5rem;
    font-size: 0.8rem;
  }
}

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

.dock-zone.active {
  opacity: 1;
}

#dock-zone-top {
  top: 0;
  left: 0;
  right: 0;
  height: 15%;
}

#dock-zone-right {
  top: 0;
  right: 0;
  bottom: 0;
  width: 15%;
}

#dock-zone-bottom {
  bottom: 0;
  left: 0;
  right: 0;
  height: 15%;
}

#dock-zone-left {
  top: 0;
  left: 0;
  bottom: 0;
  width: 15%;
}
</style>