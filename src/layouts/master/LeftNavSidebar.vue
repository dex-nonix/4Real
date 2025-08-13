<template>
  <Sidebar ref="sidebarRef" v-model:visible="visible" position="left" modal :dismissable="true" :autoFocus="false" :style="{ width: '90vw', maxWidth: '18rem' }" @hide="onHide" :aria-modal="true" role="dialog" :baseZIndex="1000">
    <div class="w-full h-full overflow-y-auto overflow-x-hidden">
      <PanelMenu :model="menuItems" :router="true" :exact="true" class="w-full md:w-18rem" :pt="ptOverrides"/>
    </div>
  </Sidebar>
  <div class="hidden md:block h-full" v-if="!collapsed" aria-hidden="false">
    <div class="border-right-1 surface-border h-full overflow-hidden">
      <div class="h-full overflow-y-auto">
        <PanelMenu :model="menuItems" :router="true" :exact="true" class="w-18rem p-1" :pt="ptOverrides"/>
      </div>
    </div>
  </div>
  
</template>

<script setup>
import Sidebar from 'primevue/sidebar'
import PanelMenu from 'primevue/panelmenu'
import { computed, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAppShell } from './useAppShell'
import { leftNavItems } from './NavItems'

const props = defineProps({ pinned: { type: Boolean, default: false } })

const { state } = useAppShell()
const visible = computed({
  get: () => state.leftOpen && !props.pinned,
  set: (v) => { state.leftOpen = v }
})

const collapsed = computed(() => state.leftCollapsed)
const router = useRouter()

// Attach explicit router commands to leaf items; close mobile sidebar after nav
function enhance(items) {
  return items.map(item => {
    const copy = { ...item }
    if (copy.items && copy.items.length) {
      copy.items = enhance(copy.items)
    } else if (copy.to) {
      copy.command = () => {
        // Close mobile sidebar first to avoid focusing aria-hidden nodes
        if (typeof window !== 'undefined' && window.innerWidth < 768) {
          state.leftOpen = false
        }
        router.push(copy.to)
        nextTick(() => {
          const main = document.getElementById('app-main')
          if (main && typeof main.focus === 'function') main.focus()
        })
      }
    }
    return copy
  })
}

const menuItems = computed(() => enhance(leftNavItems))

const sidebarRef = ref()
function onHide() {}

const ptOverrides = {
  action: {
    onMousedown: (e) => e.preventDefault()
  }
}

// no-op
</script>

<style scoped>
.w-18rem { width: 18rem; }
:deep(.p-sidebar-content) { padding: 0; overflow-x: hidden; }
</style>


