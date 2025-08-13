<template>
  <div class="flex flex-column h-full">
    <TopBar />
    <div class="flex flex-1 overflow-hidden">
      <LeftNavSidebar :pinned="false" />
      <div class="flex-1 overflow-auto">
        <slot />
      </div>
      <RightToolsSidebar />
    </div>
  </div>
</template>

<script setup>
import TopBar from './TopBar.vue'
import LeftNavSidebar from './LeftNavSidebar.vue'
import RightToolsSidebar from './RightToolsSidebar.vue'
</script>


