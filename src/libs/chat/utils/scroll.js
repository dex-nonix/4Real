// src/components/chat/utils/scroll.js

export function isAtBottom(container, threshold = 10) {
  if (!container) return true
  const { scrollTop, scrollHeight, clientHeight } = container
  return scrollHeight - clientHeight - scrollTop <= threshold
}

export function scrollToBottom(container) {
  if (!container) return
  container.scrollTop = container.scrollHeight
}


