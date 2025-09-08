<template>
  <div class="hidden md:block h-full" aria-hidden="false">
    <div class="border-right-1 surface-border h-full overflow-hidden">
      <div class="h-full overflow-y-auto">
        <PanelMenu :model="menuItems" :router="true" :exact="true" class="w-18rem p-1" :pt="ptOverrides"/>
      </div>
    </div>
  </div>
</template>

<script setup>
import PanelMenu from 'primevue/panelmenu'
import {computed, nextTick} from 'vue'
import {useRouter} from 'vue-router'
import {useAppShell} from './useAppShell.js'
import {leftNavItems} from './NavItems.js'

const props = defineProps({pinned: {type: Boolean, default: false}});

const {state} = useAppShell();
const router = useRouter();

// Attach explicit router commands to leaf items; close mobile sidebar after nav
function enhance(items) {
  return items.map(item => {
    const copy = {...item}
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
const ptOverrides = {
  action: {
    onMousedown: (e) => e.preventDefault()
  }
}
</script>
