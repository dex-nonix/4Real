<template>
  <component :is="layout">
    <router-view />
  </component>
  <Toast />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MasterLayout from '@/layouts/master/MasterLayout.vue'
import AltLayout from '@/layouts/AltLayout.vue'
import Toast from 'primevue/toast'

const route = useRoute()
const layouts = { master: MasterLayout, alt: AltLayout }

const layoutName = computed(() => route.meta.layout || 'master')
const layout = computed(() => layouts[layoutName.value] || MasterLayout)
</script>

