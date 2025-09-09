<template>
  <div class="page h-full overflow-auto">
    <slot />
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch, toRefs } from 'vue'
import { useAdvancedLayout } from '@nonix-advanced-layout/useAdvancedLayout.js'

const props = defineProps({
  title: { type: String, default: undefined },
  back: { type: Boolean, default: false },
  actions: { type: Array, default: undefined },
  showRightToggle: { type: Boolean, default: false },
  onBack: { type: Function, default: undefined }
})

const { setTitle, clearActions, addAction, state } = useAdvancedLayout()
const { title, back, actions, showRightToggle, onBack } = toRefs(props)

function applyHeader() {
  if (title.value) {
    setTitle(title.value)
  }
  clearActions()
  if (actions.value && actions.value.length > 0) {
    actions.value.forEach(action => addAction(action))
  }
  // Update state for back, showRightToggle, onBack
  if (back.value !== undefined) {
    state.header.back = back.value
  }
  if (showRightToggle.value !== undefined) {
    state.header.showRightToggle = showRightToggle.value
  }
  if (onBack.value !== undefined) {
    state.header.onBack = onBack.value
  }
}

function resetHeader() {
  setTitle('')
  clearActions()
  state.header.back = false
  state.header.showRightToggle = false
  state.header.onBack = null
}

onMounted(applyHeader)
watch([title, back, actions, showRightToggle, onBack], applyHeader, { deep: true })
onBeforeUnmount(() => resetHeader())
</script>


