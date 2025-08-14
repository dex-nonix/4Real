<template>
  <div class="chat-composer flex align-items-center gap-2">
    <Textarea v-model="draft" autoResize class="w-full" :placeholder="placeholder" @keydown.enter.exact.prevent="send" @keydown.enter.shift.stop />
    <Button label="Send" icon="pi pi-send" @click="send" :disabled="sending || !canSend" />
    <RetryButton :disabled="sending || !sessionId" @retry="$emit('retry')" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import RetryButton from '@/libs/chat/composer/RetryButton.vue'

const props = defineProps({
  sessionId: { type: [Number, String], default: null },
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Type a message...' }
})

const emit = defineEmits(['update:modelValue','send','retry'])

const draft = ref(props.modelValue)
const sending = ref(false)

watch(() => props.modelValue, v => { if (v !== draft.value) draft.value = v })
watch(draft, v => emit('update:modelValue', v))

const canSend = computed(() => !!draft.value && !!props.sessionId)

async function send() {
  if (!canSend.value || sending.value) return
  sending.value = true
  try {
    emit('send', { text: draft.value })
    draft.value = ''
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.chat-composer { width: 100%; }
</style>


