// Nonix Chat Library
// Main entry point for the chat system

// Page/View Components (used once per route)
export { default as ChatView } from './ChatView.vue'

// Core Reusable Components (can be used multiple times)
export { default as Chat } from './components/Chat.vue'
export { default as ChatSessionBar } from './components/ChatSessionBar.vue'
export { default as ChatHeader } from './components/ChatHeader.vue'
export { default as ChatMessageContainer } from './components/ChatMessageContainer.vue'

// Message Type Components
export { default as TextMessage } from './components/message-types/TextMessage.vue'
export { default as SystemMessage } from './components/message-types/SystemMessage.vue'
export { default as ToolMessage } from './components/message-types/ToolMessage.vue'
export { default as UserMessage } from './components/message-types/UserMessage.vue'

// Dialog Components
export { default as PersonaSelectionDialog } from './components/PersonaSelectionDialog.vue'
export { default as HistoryManagementDialog } from './components/HistoryManagementDialog.vue'

// Utilities
export { default as ChatMessageTypeManager } from './components/ChatMessageTypeManager.js'

// Services
export { default as ChatRuntimeService } from './services/ChatRuntimeService.js'

// Examples
export { default as ChatExample } from './examples/ChatExample.vue'
export { default as ChatMessageExample } from './examples/ChatMessageExample.vue'
