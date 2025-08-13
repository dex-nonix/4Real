<template>
<Sidebar ref="sidebarRef" v-model:visible="visible" position="left" modal :dismissable="true" :style="{ width: '90vw', maxWidth: '18rem' }" @hide="onHide" :aria-modal="true" role="dialog" :baseZIndex="1000">
    <div class="w-full h-full overflow-y-auto overflow-x-hidden" @mousedown.capture="preBlur">
      <PanelMenu :model="menuItems" class="w-full md:w-18rem"/>
    </div>
  </Sidebar>
  <div class="hidden md:block h-full" v-if="!collapsed" aria-hidden="false">
    <div class="border-right-1 surface-border h-full overflow-hidden">
      <div class="h-full overflow-y-auto" @mousedown.capture="preBlur">
        <PanelMenu :model="menuItems" class="w-18rem p-1"/>
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

// Attach explicit router commands to leaf items; close mobile sidebar after nav
function enhance(items) {
  return items.map(item => {
    const copy = { ...item }
    if (copy.items && copy.items.length) {
      copy.items = enhance(copy.items)
    } else if (copy.to) {
      copy.command = () => {
        const el = document.activeElement
        if (el && typeof el.blur === 'function') el.blur()
        router.push(copy.to)
        if (typeof window !== 'undefined' && window.innerWidth < 768) {
          state.leftOpen = false
        }
      }
    }
    return copy
  })
}

const menuItems = computed(() => enhance(leftNavItems))

const sidebarRef = ref()
function onHide() {
  // Ensure no focused element remains inside aria-hidden container
  const el = document.activeElement
  if (el && typeof el.blur === 'function') el.blur()
}

watch(visible, (v) => {
  if (!v) {
    // Defer blur to after DOM updates when closing via state toggle
    setTimeout(() => {
      const el = document.activeElement
      if (el && typeof el.blur === 'function') el.blur()
    }, 0)
  }
})

function preBlur() {
  const el = document.activeElement
  if (el && typeof el.blur === 'function') el.blur()
}

// no-op
</script>

<style scoped>
.w-18rem { width: 18rem; }
:deep(.p-sidebar-content) { padding: 0; overflow-x: hidden; }
</style>


