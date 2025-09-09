<template>
  <!-- Layout container with sidebar inside -->
  <div class="layout-container" :class="{ 'sidebar-pinned': isSidebarPinned }">
    <!-- Main layout content -->
    <div class="main-content flex flex-col">
      <TopBar />
      <div class="flex flex-1 overflow-hidden">
        <LeftNavSidebar :pinned="false" />
        <main id="app-main" tabindex="-1" class="flex-1 overflow-auto" aria-label="Main Content">
          <slot />
        </main>
      </div>
    </div>

    <!-- Sidebar positioned inside the layout container -->
    <RightToolsSidebar />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import TopBar from '@nonix-master-layout/TopBar.vue'
import LeftNavSidebar from '@nonix-advanced-layout/LeftNavSidebar.vue'
import RightToolsSidebar from './RightToolsSidebar.vue'
import { useAppShell } from './useAppShell.js'

const { state } = useAppShell()

// Mobile detection
const isMobile = ref(false)
const updateMobileState = () => {
  isMobile.value = window.innerWidth < 768
}

// Check if sidebar should push layout aside
const isSidebarPinned = computed(() => {
  return state.rightPinned && !isMobile.value
})

// Initialize mobile state
if (typeof window !== 'undefined') {
  updateMobileState()
  window.addEventListener('resize', updateMobileState)
}
</script>

<style scoped>
.layout-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
}

.main-content {
  flex: 1;
  height: 100%;
  min-width: 0; /* Allow flex item to shrink */
  transition: flex-basis 0.3s ease;
  display: flex;
  flex-direction: column;
}

/* When sidebar is pinned, main content takes remaining space */
.layout-container.sidebar-pinned .main-content {
  flex: 1;
  flex-basis: calc(100% - 450px);
}

/* Mobile: always take full width */
@media (max-width: 767px) {
  .layout-container.sidebar-pinned .main-content {
    flex-basis: 100%;
  }
}
</style>


