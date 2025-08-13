<template>
  <div class="page">
    <slot />
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch, toRefs } from 'vue'
import { usePageHeader } from '@/layouts/master/usePageHeader'

const props = defineProps({
  title: { type: String, default: undefined },
  back: { type: Boolean, default: false },
  actions: { type: Array, default: undefined },
  showRightToggle: { type: Boolean, default: false },
  onBack: { type: Function, default: undefined }
})

const { setHeader, resetHeader } = usePageHeader()
const { title, back, actions, showRightToggle, onBack } = toRefs(props)

function applyHeader() {
  setHeader({
    title: title.value,
    back: back.value,
    actions: actions.value,
    showRightToggle: showRightToggle.value,
    onBack: onBack.value
  })
}

onMounted(applyHeader)
watch([title, back, actions, showRightToggle, onBack], applyHeader, { deep: true })
onBeforeUnmount(() => resetHeader())
</script>


