<template>
  <component :is="layout">
    <router-view :key="$route.fullPath"/>
  </component>
  <Toast position="bottom-left"/>
</template>

<script setup>
import {computed} from 'vue'
import {useRoute} from 'vue-router'
import Toast from 'primevue/toast'
import NxLayoutManager from "@nonix-dynamic/manager/NxLayoutManager.js";

const route = useRoute()
const computedLayoutName = computed(() => route.meta.layout || 'advanced')
const layout = computed(() => NxLayoutManager.getWidget(computedLayoutName.value).component)
</script>

