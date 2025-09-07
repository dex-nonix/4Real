<template>
  <!-- Layout wrapper with sidebar outside -->
  <div class="layout-wrapper">
    <!-- Main layout content (everything except sidebar) -->
    <div class="main-layout flex flex-column h-full">
      <TopBar />
      <div class="content-area flex flex-1 overflow-hidden">
        <LeftNavSidebar :pinned="false" />
        <main id="app-main" tabindex="-1" class="flex-1 overflow-auto" aria-label="Main Content">
          <slot />
        </main>
      </div>
    </div>

    <!-- Sidebar positioned outside the main layout -->
    <RightToolsSidebar />
  </div>
</template>

<script setup>
import TopBar from './TopBar.vue'
import LeftNavSidebar from './LeftNavSidebar.vue'
import RightToolsSidebar from './RightToolsSidebar.vue'
</script>


