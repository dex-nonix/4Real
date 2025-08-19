// WebSocketManager.js - Single WebSocket connection manager for the entire app
import { API_BASE_URL } from '@/env.js'

export default class WebSocketManager {
  constructor() {
    this.socket = null
    this.connectionState = 'disconnected' // 'disconnected', 'connecting', 'connected', 'reconnecting'
    this.eventBus = new EventTarget()
    this.channels = new Map() // Track all channels: channelName -> { listeners: Map, joined: boolean }
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.queuedChannels = null // Queue for channels to join when connection is stable
    
    this._initWebSocket()
  }

  // Initialize WebSocket connection
  async _initWebSocket() {
    try {
      // Import SocketIO client
      const socketIOClient = await import('socket.io-client')
      const io = socketIOClient.io
      
      // Connect directly to backend server (not through Vite proxy)
      // Vite proxy only handles HTTP, not WebSocket connections
      const wsUrl = 'http://localhost:5000'
      this.socket = io(wsUrl, {
        path: '/api/ws',  // Connect to the /api/ws path configured in backend
        transports: ['websocket', 'polling'],
        autoConnect: true,
        reconnection: true,
        reconnectionDelay: this.reconnectDelay,
        reconnectionAttempts: this.maxReconnectAttempts
      })
      
      this._setupEventHandlers()
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error)
      this.connectionState = 'disconnected'
      this.eventBus.dispatchEvent(new CustomEvent('websocket:init_failed', { detail: error }))
    }
  }

  // Set up Socket.IO event handlers
  _setupEventHandlers() {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('🔌 WebSocket connected to backend')
      this.connectionState = 'connected'
      this.reconnectAttempts = 0
      this.eventBus.dispatchEvent(new CustomEvent('websocket:connected'))
      this._rejoinAllChannels()
      this._processQueuedChannels() // Process queued channel joins after successful connection
    })

    this.socket.on('disconnect', () => {
      console.log('🔌 WebSocket disconnected from backend')
      this.connectionState = 'disconnected'
      this.eventBus.dispatchEvent(new CustomEvent('websocket:disconnected'))
    })

    this.socket.on('connect_error', (error) => {
      console.error('🔌 WebSocket connection error:', error)
      this.connectionState = 'reconnecting'
      this.reconnectAttempts++
      this.eventBus.dispatchEvent(new CustomEvent('websocket:reconnecting', { detail: { attempt: this.reconnectAttempts, error } }))
    })

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('🔌 WebSocket reconnected after', attemptNumber, 'attempts')
      this.connectionState = 'connected'
      this.reconnectAttempts = 0
      this.eventBus.dispatchEvent(new CustomEvent('websocket:reconnected', { detail: { attempt: attemptNumber } }))
      this._rejoinAllChannels()
      this._processQueuedChannels() // Process queued channel joins after successful reconnection
    })

    this.socket.on('reconnect_failed', () => {
      console.error('🔌 WebSocket reconnection failed after', this.maxReconnectAttempts, 'attempts')
      this.connectionState = 'disconnected'
      this.eventBus.dispatchEvent(new CustomEvent('websocket:reconnect_failed'))
    })
  }

  // Join a specific WebSocket channel
  joinChannel(channel) {
    if (!this.socket || !this.socket.connected || this.connectionState !== 'connected') {
      console.warn('WebSocket not connected, cannot join channel:', channel)
      // Queue the channel join for when connection is stable
      this._queueChannelJoin(channel)
      return false
    }
    
    // Track the channel
    if (!this.channels.has(channel)) {
      this.channels.set(channel, { listeners: new Map(), joined: true })
    } else {
      this.channels.get(channel).joined = true
    }
    
    this.socket.emit('join_channel', { channel })
    console.log('🔌 Joined WebSocket channel:', channel)
    return true
  }

  // Queue channel join for when connection is stable
  _queueChannelJoin(channel) {
    if (!this.queuedChannels) {
      this.queuedChannels = new Set()
    }
    this.queuedChannels.add(channel)
    console.log('🔌 Queued channel join for later:', channel)
  }

  // Process queued channel joins when connection is stable
  _processQueuedChannels() {
    if (this.queuedChannels && this.queuedChannels.size > 0) {
      console.log('🔌 Processing queued channel joins...')
      this.queuedChannels.forEach(channel => {
        this.joinChannel(channel)
      })
      this.queuedChannels.clear()
    }
  }

  // Leave a specific WebSocket channel
  leaveChannel(channel) {
    if (!this.socket || !this.socket.connected) {
      return false
    }
    
    const channelData = this.channels.get(channel)
    if (channelData) {
      channelData.joined = false
      // Don't remove the channel completely - keep listeners for reconnection
    }
    
    console.log('🔌 Left WebSocket channel:', channel)
    return true
  }

  // Listen to events from a specific channel
  onChannelEvent(channel, event, callback) {
    if (!this.socket || !this.socket.connected) {
      console.warn('WebSocket not connected, cannot listen to events')
      return () => {} // Return no-op unsubscribe function
    }
    
    const eventKey = `${channel}:${event}`
    
    // Store the listener for reconnection purposes
    if (!this.channels.has(channel)) {
      this.channels.set(channel, { listeners: new Map(), joined: false })
    }
    this.channels.get(channel).listeners.set(event, callback)
    
    // Listen to the event
    this.socket.on(eventKey, callback)
    
    console.log('🔌 Listening to channel event:', eventKey)
    
    // Return unsubscribe function
    return () => {
      this.socket.off(eventKey, callback)
      const channelData = this.channels.get(channel)
      if (channelData) {
        channelData.listeners.delete(event)
      }
    }
  }

  // Send event to a specific channel
  emitToChannel(channel, event, data) {
    if (!this.socket || !this.socket.connected) {
      console.warn('WebSocket not connected, cannot emit event')
      return false
    }
    
    this.socket.emit('channel_message', {
      channel,
      data: { event, data }
    })
    
    console.log('🔌 Emitted to channel:', channel, 'event:', event, 'data:', data)
    return true
  }

  // Alias for emitToChannel (matches backend naming)
  sendToChannel(channel, event, data) {
    return this.emitToChannel(channel, event, data)
  }

  // Send event to a specific room
  sendToRoom(room, event, data) {
    if (!this.socket || !this.socket.connected) {
      console.warn('WebSocket not connected, cannot send to room')
      return false
    }
    
    this.socket.emit(event, data, room)
    
    console.log('🔌 Sent to room:', room, 'event:', event, 'data:', data)
    return true
  }

  // Rejoin all channels after reconnection
  _rejoinAllChannels() {
    console.log('🔌 Rejoining all channels after reconnection...')
    
    this.channels.forEach((channelData, channelName) => {
      if (channelData.joined) {
        // Rejoin the channel
        this.socket.emit('join_channel', { channel: channelName })
        console.log('🔌 Rejoined channel:', channelName)
        
        // Reattach all event listeners for this channel
        channelData.listeners.forEach((listener, event) => {
          const eventKey = `${channelName}:${event}`
          this.socket.on(eventKey, listener)
          console.log('🔌 Reattached listener for:', eventKey)
        })
      }
    })
  }

  // Get all subscribed channels
  getSubscribedChannels() {
    return Array.from(this.channels.keys()).filter(channel => this.channels.get(channel).joined)
  }

  // Check if WebSocket is connected and stable
  isConnected() {
    return this.socket && this.socket.connected && this.connectionState === 'connected'
  }

  // Check if WebSocket is in a stable state (connected or reconnecting)
  isStable() {
    return this.connectionState === 'connected' || this.connectionState === 'reconnecting'
  }

  // Get connection state
  getConnectionState() {
    return this.connectionState
  }

  // Manual reconnect
  async reconnect() {
    if (this.connectionState === 'reconnecting') return
    
    console.log('🔌 Manual reconnection initiated...')
    this.connectionState = 'reconnecting'
    this.eventBus.dispatchEvent(new CustomEvent('websocket:manual_reconnect'))
    
    try {
      if (this.socket) {
        this.socket.disconnect()
      }
      await this._initWebSocket()
    } catch (error) {
      console.error('Manual reconnection failed:', error)
      this.connectionState = 'disconnected'
      this.eventBus.dispatchEvent(new CustomEvent('websocket:manual_reconnect_failed', { detail: error }))
    }
  }

  // Clean up WebSocket resources
  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.connectionState = 'disconnected'
    this.channels.clear()
    this.queuedChannels = null // Clear queued channels on disconnect
    console.log('🔌 WebSocket disconnected and cleaned up')
  }

  // Add event listener for WebSocket events
  addEventListener(event, callback) {
    this.eventBus.addEventListener(event, callback)
  }

  // Remove event listener
  removeEventListener(event, callback) {
    this.eventBus.removeEventListener(event, callback)
  }
}
