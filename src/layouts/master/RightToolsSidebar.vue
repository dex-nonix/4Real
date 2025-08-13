<template>
  <Sidebar v-model:visible="visible" position="right" modal :dismissable="true">
    <slot>
      <div class="p-3">
        <h3 class="m-0 mb-2">Tools</h3>
        <p class="m-0 text-600">Add contextual tools here.</p>
      </div>
    </slot>
  </Sidebar>
</template>

<script setup>
import Sidebar from 'primevue/sidebar'
import { computed } from 'vue'
import { useAppShell } from './useAppShell'

const { state } = useAppShell()
const visible = computed({
  get: () => state.rightOpen,
  set: (v) => { state.rightOpen = v }
})
</script>


