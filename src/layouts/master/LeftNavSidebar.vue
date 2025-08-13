<template>
  <Sidebar v-model:visible="visible" position="left" modal :dismissable="true">
    <PanelMenu :model="navItems" :exact="true" class="w-18rem"/>
  </Sidebar>
  <div class="hidden md:flex h-full">
    <div v-show="!collapsed" class="border-right-1 surface-border h-full">
      <PanelMenu :model="navItems" :exact="true" class="w-18rem p-2"/>
    </div>
    <div class="border-right-1 surface-border h-full flex align-items-center justify-content-center px-2 cursor-pointer"
         title="Toggle navigation"
         @click="toggleLeft">
      <i class="pi pi-bars"></i>
    </div>
  </div>
  
</template>

<script setup>
import Sidebar from 'primevue/sidebar'
import PanelMenu from 'primevue/panelmenu'
import { computed } from 'vue'
import { useAppShell } from './useAppShell'
import { leftNavItems } from './NavItems'

const props = defineProps({ pinned: { type: Boolean, default: false } })

const { state, toggleLeft } = useAppShell()
const visible = computed({
  get: () => state.leftOpen && !props.pinned,
  set: (v) => { state.leftOpen = v }
})

const collapsed = computed(() => state.leftCollapsed)
const navItems = leftNavItems
</script>

<style scoped>
.w-18rem { width: 18rem; }
</style>


