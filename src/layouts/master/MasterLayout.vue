<template>
  <div class="flex flex-column h-full">
    <TopBar />
    <div class="flex flex-1 overflow-hidden">
      <LeftNavSidebar :pinned="false" />
      <main id="app-main" tabindex="-1" class="flex-1 overflow-auto" aria-label="Main Content">
        <slot />
      </main>
      <RightToolsSidebar />
    </div>
  </div>
</template>

<script setup>
import TopBar from './TopBar.vue'
import LeftNavSidebar from './LeftNavSidebar.vue'
import RightToolsSidebar from './RightToolsSidebar.vue'
</script>


