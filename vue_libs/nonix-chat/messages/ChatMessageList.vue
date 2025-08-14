<template>
  <div ref="scroller" class="chat-message-list p-2" @scroll="handleScroll">
    <div v-for="m in messages" :key="m.id || m.created_at">
      <MessageBubble v-if="m.role !== 'tool'" :role="m.role" :content="m.content_json" />
      <ToolCallMessage v-else :content="m.content_json" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'
import ToolCallMessage from './ToolCallMessage.vue'
import { isAtBottom, scrollToBottom } from '../utils/scroll.js'

const props = defineProps({
  messages: { type: Array, default: () => [] }
})

const scroller = ref(null)
let stickToBottom = true

function handleScroll() {
  stickToBottom = isAtBottom(scroller.value)
}

watch(() => props.messages?.length, async () => {
  await nextTick()
  if (stickToBottom) scrollToBottom(scroller.value)
})
</script>

<style scoped>
.chat-message-list { width: 100%; height: 280px; overflow: auto; background: var(--surface-0); }
</style>


