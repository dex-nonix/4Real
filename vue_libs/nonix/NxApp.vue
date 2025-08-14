<template>
  <component :is="layout">
    <router-view :key="$route.fullPath"/>
  </component>
  <Toast/>
</template>

<script setup>
import {computed} from 'vue'
import {useRoute} from 'vue-router'
import Toast from 'primevue/toast'
import LayoutManager from "./widget-manager/LayoutManager.js";

const route = useRoute()
const computedLayoutName = computed(() => route.meta.layout || 'master')
const layout = computed(() => LayoutManager.getWidget(computedLayoutName.value).component)
</script>

