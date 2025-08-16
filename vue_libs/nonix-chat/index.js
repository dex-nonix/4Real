// Main entry point for nonix-chat library
// Exporting the working chat components that integrate with backend

// Main chat components
export { default as Chat } from './components/Chat.vue'
export { default as ChatWidget } from './ChatWidget.vue'

// Message type components
export { default as TextMessage } from './components/message-types/TextMessage.vue'
export { default as SystemMessage } from './components/message-types/SystemMessage.vue'
export { default as ToolMessage } from './components/message-types/ToolMessage.vue'
export { default as UserMessage } from './components/message-types/UserMessage.vue'

// Message type manager
export { default as ChatMessageTypeManager } from './components/ChatMessageTypeManager.js'

// Example components for development and testing
export { default as ChatExample } from './components/ChatExample.vue'
export { default as ChatMessageExample } from './components/ChatMessageExample.vue'

// Utility components
export { default as ChatHeader } from './components/ChatHeader.vue'
export { default as ChatMessages } from './components/ChatMessages.vue'
export { default as ChatMessageInput } from './components/ChatMessageInput.vue'
export { default as ChatSessionBar } from './components/ChatSessionBar.vue'

// Backend service
export { default as ChatRuntimeService } from './services/ChatRuntimeService.js'
