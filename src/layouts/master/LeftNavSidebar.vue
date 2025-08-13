<template>
  <Sidebar v-model:visible="visible" position="left" modal :dismissable="true">
    <PanelMenu :model="navItems" :exact="true" class="w-18rem"/>
  </Sidebar>
  <div v-if="pinned" class="hidden md:block border-right-1 surface-border h-full">
    <PanelMenu :model="navItems" :exact="true" class="w-18rem p-2"/>
  </div>
  
</template>

<script setup>
import Sidebar from 'primevue/sidebar'
import PanelMenu from 'primevue/panelmenu'
import { computed } from 'vue'
import { useAppShell } from './useAppShell'
import { leftNavItems } from './NavItems'

const props = defineProps({ pinned: { type: Boolean, default: false } })

const { state } = useAppShell()
const visible = computed({
  get: () => state.leftOpen && !props.pinned,
  set: (v) => { state.leftOpen = v }
})

const navItems = leftNavItems
</script>

<style scoped>
.w-18rem { width: 18rem; }
</style>


