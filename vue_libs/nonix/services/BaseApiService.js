// BaseApiService.js - minimal fetch-based HTTP layer with WebSocket support
import { API_BASE_URL } from '@/env.js'

export default class BaseApiService {
  constructor(options = {}) {
    const { defaultHeaders = {}, onRequest, onResponse, onError, enableWebSocket = true } = options
    this.baseURL = API_BASE_URL.replace(/\/$/, '')
    this.defaultHeaders = { 'Content-Type': 'application/json', ...defaultHeaders }
    this.onRequest = onRequest
    this.onResponse = onResponse
    this.onError = onError
    
    // WebSocket initialization
    this.socket = null
    this.channels = new Set() // Track subscribed channels
    this.eventListeners = new Map() // Track event listeners by channel
    
    if (enableWebSocket) {
      this._initWebSocket()
    }
  }

  // Initialize WebSocket connection
  _initWebSocket() {
    try {
      // Import SocketIO client dynamically to avoid SSR issues
      import('socket.io-client').then(({ io }) => {
        // Extract WebSocket URL from API base URL
        const wsUrl = this.baseURL.replace('http://', 'ws://').replace('https://', 'wss://')
        this.socket = io(`${wsUrl}/api/ws/`, {
          transports: ['websocket', 'polling'],
          autoConnect: true,
          reconnection: true,
          reconnectionDelay: 1000,
          reconnectionAttempts: 5
        })
        
        // Set up connection event handlers
        this.socket.on('connect', () => {
          console.log('🔌 WebSocket connected to backend')
        })
        
        this.socket.on('disconnect', () => {
          console.log('🔌 WebSocket disconnected from backend')
        })
        
        this.socket.on('connect_error', (error) => {
          console.error('🔌 WebSocket connection error:', error)
        })
        
        // Re-join channels on reconnection
        this.socket.on('connect', () => {
          this.channels.forEach(channel => {
            this.socket.emit('join_channel', { channel })
          })
        })
      }).catch(error => {
        console.warn('WebSocket not available:', error)
      })
    } catch (error) {
      console.warn('WebSocket initialization failed:', error)
    }
  }

  // WebSocket Methods

  /**
   * Join a specific WebSocket channel
   * @param {string} channel - Channel name (e.g., 'chat/123/456')
   * @returns {boolean} - Success status
   */
  joinChannel(channel) {
    if (!this.socket || !this.socket.connected) {
      console.warn('WebSocket not connected, cannot join channel:', channel)
      return false
    }
    
    this.socket.emit('join_channel', { channel })
    this.channels.add(channel)
    console.log('🔌 Joined WebSocket channel:', channel)
    return true
  }

  /**
   * Leave a specific WebSocket channel
   * @param {string} channel - Channel name to leave
   * @returns {boolean} - Success status
   */
  leaveChannel(channel) {
    if (!this.socket || !this.socket.connected) {
      return false
    }
    
    // Remove event listeners for this channel
    this._removeChannelListeners(channel)
    
    // Remove from tracked channels
    this.channels.delete(channel)
    
    console.log('🔌 Left WebSocket channel:', channel)
    return true
  }

  /**
   * Listen to events from a specific channel
   * @param {string} channel - Channel name
   * @param {string} event - Event name
   * @param {Function} callback - Event handler function
   * @returns {Function} - Unsubscribe function
   */
  onChannelEvent(channel, event, callback) {
    if (!this.socket || !this.socket.connected) {
      console.warn('WebSocket not connected, cannot listen to events')
      return () => {} // Return no-op unsubscribe function
    }
    
    const eventKey = `${channel}:${event}`
    const listener = (data) => {
      callback(data)
    }
    
    // Store listener for cleanup
    if (!this.eventListeners.has(channel)) {
      this.eventListeners.set(channel, new Map())
    }
    this.eventListeners.get(channel).set(event, listener)
    
    // Listen to the event
    this.socket.on(eventKey, listener)
    
    console.log('🔌 Listening to channel event:', eventKey)
    
    // Return unsubscribe function
    return () => {
      this.socket.off(eventKey, listener)
      const channelListeners = this.eventListeners.get(channel)
      if (channelListeners) {
        channelListeners.delete(event)
      }
    }
  }

  /**
   * Send event to a specific channel
   * @param {string} channel - Channel name
   * @param {string} event - Event name
   * @param {any} data - Event data
   * @returns {boolean} - Success status
   */
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

  /**
   * Alias for emitToChannel (matches backend naming)
   * @param {string} channel - Channel name
   * @param {string} event - Event name
   * @param {any} data - Event data
   * @returns {boolean} - Success status
   */
  sendToChannel(channel, event, data) {
    return this.emitToChannel(channel, event, data)
  }

  /**
   * Send event to a specific room
   * @param {string} room - Room name
   * @param {string} event - Event name
   * @param {any} data - Event data
   * @returns {boolean} - Success status
   */
  sendToRoom(room, event, data) {
    if (!this.socket || !this.socket.connected) {
      console.warn('WebSocket not connected, cannot send to room')
      return false
    }
    
    this.socket.emit(event, data, room)
    
    console.log('🔌 Sent to room:', room, 'event:', event, 'data:', data)
    return true
  }

  /**
   * Get all subscribed channels
   * @returns {Array<string>} - Array of channel names
   */
  getSubscribedChannels() {
    return Array.from(this.channels)
  }

  /**
   * Check if WebSocket is connected
   * @returns {boolean} - Connection status
   */
  isWebSocketConnected() {
    return this.socket && this.socket.connected
  }

  /**
   * Clean up WebSocket resources
   */
  disconnect() {
    if (this.socket) {
      // Remove all event listeners
      this.eventListeners.forEach((channelListeners, channel) => {
        this._removeChannelListeners(channel)
      })
      
      // Disconnect socket
      this.socket.disconnect()
      this.socket = null
      this.channels.clear()
      this.eventListeners.clear()
      
      console.log('🔌 WebSocket disconnected and cleaned up')
    }
  }

  // Private helper method to remove channel listeners
  _removeChannelListeners(channel) {
    const channelListeners = this.eventListeners.get(channel)
    if (channelListeners) {
      channelListeners.forEach((listener, event) => {
        const eventKey = `${channel}:${event}`
        if (this.socket) {
          this.socket.off(eventKey, listener)
        }
      })
      channelListeners.clear()
    }
    this.eventListeners.delete(channel)
  }

  // Base path for derived services; subclasses can override
  basePath() {
    return ''
  }

  // Scope a relative path to the service's basePath
  scopePath(path) {
    const bp = this.basePath() || ''
    if (!bp) return path
    if (path === '/' || path === '' || path == null) return bp
    if (typeof path !== 'string') return bp
    if (path.startsWith('/')) return `${bp}${path}`
    return `${bp}/${path}`
  }

  buildUrl(path, query) {
    const base = `${this.baseURL}${path.startsWith('/') ? '' : '/'}${path}`
    if (!query || typeof query !== 'object') return base
    const params = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
      if (value === null || value === undefined) return
      if (Array.isArray(value)) {
        value.forEach(v => params.append(key, String(v)))
      } else {
        params.append(key, String(value))
      }
    })
    const qs = params.toString()
    return qs ? `${base}?${qs}` : base
  }

  async request(method, path, options = {}) {
    const { query, body, headers = {}, signal } = options
    const scoped = this.scopePath(path)
    const url = this.buildUrl(scoped, query)
    const finalHeaders = { ...this.defaultHeaders, ...headers }
    
    const init = { method, headers: finalHeaders, signal }
    if (body !== undefined) {
      if (typeof FormData !== 'undefined' && body instanceof FormData) {
        // Let the browser set multipart boundaries
        delete init.headers['Content-Type']
        init.body = body
      } else {
        init.body = JSON.stringify(body)
      }
    }

    try {
      if (this.onRequest) await this.onRequest({ method, url, init })
      const res = await window.fetch(url, init)
      const contentType = res.headers.get('content-type') || ''
      const isJson = contentType.includes('application/json')
      const data = isJson ? await res.json().catch(() => null) : await res.text().catch(() => null)
      const result = { status: res.status, ok: res.ok, data, headers: res.headers }
      if (this.onResponse) await this.onResponse(result)
      if (!res.ok) {
        const message = (data && (data.message || data.error)) || res.statusText || 'Request failed'
        const error = { status: res.status, message, data }
        if (this.onError) await this.onError(error)
        throw error
      }
      return result
    } catch (err) {
      if (this.onError && (!err || !err.status)) await this.onError(err)
      throw err
    }
  }

  get(path, options) { return this.request('GET', path, options) }
  post(path, body, options = {}) { return this.request('POST', path, { ...options, body }) }
  put(path, body, options = {}) { return this.request('PUT', path, { ...options, body }) }
  patch(path, body, options = {}) { return this.request('PATCH', path, { ...options, body }) }
  delete(path, options) { return this.request('DELETE', path, options) }
}


