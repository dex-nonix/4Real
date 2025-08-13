<template>
  <Sidebar ref="sidebarRef" v-model:visible="visible" position="left" modal :dismissable="true" :style="{ width: '90vw', maxWidth: '18rem' }" @hide="onHide">
    <div class="w-full h-full overflow-y-auto overflow-x-hidden">
      <PanelMenu :model="menuItems" :router="true" :exact="true" class="w-full md:w-18rem"/>
    </div>
  </Sidebar>
  <div class="hidden md:block h-full" v-if="!collapsed">
    <div class="border-right-1 surface-border h-full overflow-hidden">
      <div class="h-full overflow-y-auto">
        <PanelMenu :model="menuItems" :router="true" :exact="true" class="w-18rem p-1"/>
      </div>
    </div>
  </div>
  
</template>

<script setup>
import Sidebar from 'primevue/sidebar'
import PanelMenu from 'primevue/panelmenu'
import { computed, ref, watch } from 'vue'
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

// Ensure clicks on leaf items close the mobile sidebar
function attachCommands(items) {
  return items.map(item => {
    const copy = { ...item }
    if (copy.items && copy.items.length) {
      copy.items = attachCommands(copy.items)
    } else if (copy.to) {
      copy.command = () => {
        router.push(copy.to)
        state.leftOpen = false
      }
    }
    return copy
  })
}

const menuItems = computed(() => attachCommands(leftNavItems))

const sidebarRef = ref()
function onHide() {
  // Ensure no focused element remains inside aria-hidden container
  try { if (document.activeElement) document.activeElement.blur() } catch {}
}

watch(visible, (v) => {
  if (!v) {
    // Defer blur to after DOM updates when closing via state toggle
    setTimeout(() => {
      try { if (document.activeElement) document.activeElement.blur() } catch {}
    }, 0)
  }
})
</script>

<style scoped>
.w-18rem { width: 18rem; }
:deep(.p-sidebar-content) { padding: 0; overflow-x: hidden; }
</style>


