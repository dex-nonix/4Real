<template>
  <div class="flex align-items-center justify-content-between px-3 py-2 border-bottom-1 surface-border" role="banner">
    <div class="flex align-items-center gap-2">
      <Button id="app-burger" icon="pi pi-bars" text @click="toggleLeftAndCloseMobile" aria-label="Toggle navigation"/>
      <div id="page-header-left" class="flex align-items-center gap-2">
        <Button v-if="header.back" icon="pi pi-arrow-left" text @click="onBackClick"/>
        <h2 v-if="header.title" class="m-0 text-xl">{{ header.title }}</h2>
      </div>
    </div>
    <div class="flex align-items-center gap-2">
      <div id="page-header-right" class="flex align-items-center gap-2">
        <Menu v-if="header.actions && header.actions.length" ref="menu" :model="header.actions" :popup="true"/>
        <Button v-if="header.actions && header.actions.length" icon="pi pi-ellipsis-v" text @click="toggleMenu"
                class="md:hidden" aria-haspopup="menu"/>
      </div>
      <Button icon="pi pi-cog" text @click="toggleRight" aria-label="Toggle Chat"/>
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import {ref} from 'vue'
import {useAppShell} from './useAppShell.js'
import {usePageHeader} from './usePageHeader.js'

const {state, toggleLeft, toggleRight} = useAppShell();
const {state: header} = usePageHeader();

const menu = ref();

function toggleMenu(event) {
  menu.value.toggle(event)
}

function onBackClick() {
  typeof header.onBack === 'function' && header.onBack();
}

function toggleLeftAndCloseMobile() {
  toggleLeft()
  if (state.leftOpen === false) {
    try {
      if (document.activeElement) document.activeElement.blur()
    } catch {
    }
  }
}
</script>


