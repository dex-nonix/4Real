<template>
  <Sidebar ref="sidebarRef" v-model:visible="visible" position="left" modal :dismissable="true" :style="{ width: '90vw', maxWidth: '18rem' }" @hide="onHide">
    <div class="w-full h-full overflow-y-auto overflow-x-hidden">
      <PanelMenu :model="leftNavItems" :router="true" :exact="true" class="w-full md:w-18rem" @item-click="onItemClick"/>
    </div>
  </Sidebar>
  <div class="hidden md:block h-full" v-if="!collapsed">
    <div class="border-right-1 surface-border h-full overflow-hidden">
      <div class="h-full overflow-y-auto">
        <PanelMenu :model="leftNavItems" :router="true" :exact="true" class="w-18rem p-1" @item-click="onItemClick"/>
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

function onItemClick(event) {
  // Close sidebar after router processes
  setTimeout(() => {
    if (state.leftOpen) state.leftOpen = false
    try { if (document.activeElement) document.activeElement.blur() } catch {}
  }, 0)
}

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

// no-op
</script>

<style scoped>
.w-18rem { width: 18rem; }
:deep(.p-sidebar-content) { padding: 0; overflow-x: hidden; }
</style>


