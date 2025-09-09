<template>
  <PanelMenu
      :model="menuItems"
      :router="true"
      :exact="true"
      class="w-full" :pt="ptOverrides"/>
</template>

<script setup>
import PanelMenu from 'primevue/panelmenu'
import {computed, nextTick} from 'vue'
import {useRouter} from 'vue-router'
import {useAppShell} from '@nonix-master-layout/useAppShell.js'
import {leftNavItems} from './NavItems.js'

const props = defineProps({pinned: {type: Boolean, default: false}});

const {state} = useAppShell();
const router = useRouter();

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
