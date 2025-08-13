<template>
  <component :is="layout">
    <router-view />
  </component>

  <nav style="margin-top: 1rem;">
    <router-link to="/">Home</router-link>
    <span style="margin: 0 0.5rem;">|</span>
    <router-link to="/about">About</router-link>
    <span style="margin: 0 0.5rem;">|</span>
    <router-link to="/dynamic-form">DynamicForm</router-link>
    <span style="margin: 0 0.5rem;">|</span>
    <router-link to="/dynamic-table">DynamicTable</router-link>
  </nav>
  <hr />
  <small>Layout: {{ layoutName }}</small>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MasterLayout from '@/layouts/master/MasterLayout.vue'
import AltLayout from '@/layouts/AltLayout.vue'

const route = useRoute()
const layouts = { master: MasterLayout, alt: AltLayout }

const layoutName = computed(() => route.meta.layout || 'master')
const layout = computed(() => layouts[layoutName.value] || MasterLayout)
</script>

