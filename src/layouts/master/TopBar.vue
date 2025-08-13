<template>
  <div class="flex align-items-center justify-content-between px-3 py-2 border-bottom-1 surface-border">
    <div class="flex align-items-center gap-2">
      <Button icon="pi pi-bars" text @click="toggleLeft" />
      <div id="page-header-left" class="flex align-items-center gap-2">
        <Button v-if="header.back" icon="pi pi-arrow-left" text @click="onBackClick" />
        <h2 v-if="header.title" class="m-0 text-xl">{{ header.title }}</h2>
      </div>
    </div>
    <div class="flex align-items-center gap-2">
      <div id="page-header-right" class="flex align-items-center gap-2">
        <Menu v-if="header.actions && header.actions.length" ref="menu" :model="header.actions" :popup="true" />
        <Button v-if="header.actions && header.actions.length" icon="pi pi-ellipsis-v" text @click="toggleMenu" class="md:hidden" />
      </div>
      <Button v-if="header.showRightToggle" icon="pi pi-cog" text @click="toggleRight" />
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import { ref } from 'vue'
import { useAppShell } from './useAppShell'
import { usePageHeader } from './usePageHeader'

const { toggleLeft, toggleRight } = useAppShell()
const { state: header } = usePageHeader()

const menu = ref()
function toggleMenu(event) {
  menu.value.toggle(event)
}

function onBackClick() {
  if (typeof header.onBack === 'function') header.onBack()
}
</script>


