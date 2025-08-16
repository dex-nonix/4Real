# nonix-chat - Clean Chat Components

A modern, clean chat component library built with Vue 3 and PrimeVue.

## 🚀 Features

- **Clean Architecture**: Simple, maintainable component structure
- **Dynamic Message Types**: Extensible message rendering system
- **Modern UI**: Built with PrimeVue components
- **Type Safety**: Proper TypeScript support
- **Easy Integration**: Simple props and events

## 📦 Components

### Main Components

- **`Chat.vue`** - Main chat interface with sessions and messages
- **`ChatWidget.vue`** - Wrapped chat widget with demo data
- **`ChatWorkspace.vue`** - Workspace wrapper for integration

### Message Type Components

- **`TextMessage.vue`** - Text messages with context menu and status
- **`SystemMessage.vue`** - System notifications
- **`ToolMessage.vue`** - Tool execution display
- **`UserMessage.vue`** - User message handling

### Utility Components

- **`ChatHeader.vue`** - Chat header with user info
- **`ChatMessages.vue`** - Message list with dynamic rendering
- **`ChatMessageInput.vue`** - Message input field
- **`ChatSessionBar.vue`** - Session selection sidebar

### Management

- **`ChatMessageTypeManager.js`** - Dynamic message type registry

## 🎯 Usage

### Basic Chat Widget

```vue
<template>
  <ChatWidget 
    :instance-id="'my-chat'"
    @send-message="handleSendMessage"
    @session-selected="handleSessionSelected"
  />
</template>

<script setup>
import { ChatWidget } from '@nonix-chat'

const handleSendMessage = ({ sessionId, message }) => {
  console.log('Message sent:', message)
}

const handleSessionSelected = (sessionId) => {
  console.log('Session selected:', sessionId)
}
</script>
```

### Custom Chat Interface

```vue
<template>
  <Chat
    :sessions="sessions"
    :messages="messages"
    :current-user-id="currentUserId"
    @send-message="handleSendMessage"
  />
</template>

<script setup>
import { Chat } from '@nonix-chat'

const sessions = ref([
  { id: 1, user: { name: 'John Doe', avatarUrl: '...' } }
])

const messages = ref([
  { id: 1, type: 'text', text: 'Hello!', senderId: 'user-1', timestamp: '10:00' }
])

const currentUserId = ref('user-self')
</script>
```

### Adding Custom Message Types

```javascript
import { ChatMessageTypeManager } from '@nonix-chat'
import CustomMessage from './CustomMessage.vue'

// Register custom message type
ChatMessageTypeManager.registerMessageType('custom', CustomMessage)

// Use in messages
const message = {
  id: 1,
  type: 'custom',
  text: 'Custom message',
  senderId: 'user-1',
  timestamp: '10:00'
}
```

## 🔧 Props

### Chat.vue
- `sessions` - Array of chat sessions
- `messages` - Array of messages for current session
- `currentUserId` - ID of current user

### ChatWidget.vue
- `instanceId` - Unique identifier for chat instance
- `initialPersonaId` - Initial persona to load
- `initialSessionId` - Initial session to open
- `persistKey` - Key for persistence
- `enableLeftPanel` - Show left panel
- `enableRightPanel` - Show right panel
- `maxTabs` - Maximum number of tabs
- `readonly` - Read-only mode
- `showMCPStatus` - Show MCP status

## 📡 Events

- `send-message` - Emitted when message is sent
- `session-selected` - Emitted when session is selected
- `close-chat` - Emitted when chat is closed

## 🎨 Styling

The components use PrimeVue CSS variables and classes:
- `surface-card` - Card backgrounds
- `surface-ground` - Page backgrounds
- `text-color` - Primary text color
- `text-color-secondary` - Secondary text color
- `border-round` - Border radius utilities

## 🚫 Removed Components

The following old, complex components have been removed:
- Old `ChatWidget.vue` (complex, over-engineered)
- Old `ChatWorkspace.vue` (too many responsibilities)
- Panel components (`LeftPanel.vue`, `RightPanel.vue`, etc.)
- Old message components (`ChatMessageList.vue`, etc.)
- Complex services and hooks

## 📱 Demo

Run the demo page to see all components in action:

```vue
<template>
  <ChatDemo />
</template>

<script setup>
import ChatDemo from '@nonix-chat/demo.vue'
</script>
```

## 🔄 Migration

To migrate from the old system:

1. Replace `ChatWidget` imports with new version
2. Update props to match new interface
3. Use new event names
4. Remove complex state management
5. Use new message type system

## 📝 Development

The new system is designed to be:
- **Simple**: Easy to understand and modify
- **Extensible**: Add new message types easily
- **Maintainable**: Clear separation of concerns
- **Testable**: Components can be tested independently
