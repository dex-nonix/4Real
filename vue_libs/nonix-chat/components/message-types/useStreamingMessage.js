import { ref } from 'vue'

export function useStreamingMessage(chatService, message, enableStreaming = true) {
  const streamingContent = ref('')
  const streamingStatus = ref('streaming')
  const isTyping = ref(false)
  let unsubChunk = null
  let unsubComplete = null
  let unsubError = null

  const subscribe = () => {
    if (!enableStreaming || !chatService || !message?.id) return
    isTyping.value = (streamingStatus.value === 'streaming')
    unsubChunk = chatService.onWebSocketEvent('assistant_message_chunk', (data) => {
      if (data && data.message_id === message.id) {
        streamingContent.value += data.chunk || ''
      }
    })
    unsubComplete = chatService.onWebSocketEvent('assistant_message_complete', (data) => {
      if (data && data.message_id === message.id) {
        streamingStatus.value = 'complete'
        isTyping.value = false
      }
    })
    unsubError = chatService.onWebSocketEvent('streaming_error', (data) => {
      if (data && data.message_id === message.id) {
        streamingStatus.value = 'error'
        isTyping.value = false
      }
    })
  }

  const unsubscribe = () => {
    try { unsubChunk && unsubChunk() } catch (_) {}
    try { unsubComplete && unsubComplete() } catch (_) {}
    try { unsubError && unsubError() } catch (_) {}
    unsubChunk = unsubComplete = unsubError = null
  }

  const initFromProps = () => {
    const initialStatus = message?.status || 'streaming'
    streamingStatus.value = initialStatus
    const initialText = (message?.content_json && message.content_json.text) || ''
    streamingContent.value = initialText
    isTyping.value = (initialStatus === 'streaming')
  }

  return { streamingContent, streamingStatus, isTyping, subscribe, unsubscribe, initFromProps }
}


