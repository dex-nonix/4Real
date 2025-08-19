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
    
    // WebSocket functionality now comes from injected manager
    this.enableWebSocket = enableWebSocket
  }

  // Get WebSocket manager from app-level injection
  get wsManager() {
    // This will be provided by the app via provide/inject
    return window.__websocketManager
  }

  // WebSocket Methods - now delegate to injected manager

  /**
   * Join a specific WebSocket channel
   * @param {string} channel - Channel name (e.g., 'chat/123/456')
   * @returns {boolean} - Success status
   */
  joinChannel(channel) {
    if (!this.enableWebSocket || !this.wsManager) {
      console.warn('WebSocket not enabled or manager not available')
      return false
    }
    
    return this.wsManager.joinChannel(channel)
  }

  /**
   * Leave a specific WebSocket channel
   * @param {string} channel - Channel name to leave
   * @returns {boolean} - Success status
   */
  leaveChannel(channel) {
    if (!this.enableWebSocket || !this.wsManager) {
      return false
    }
    
    return this.wsManager.leaveChannel(channel)
  }

  /**
   * Listen to events from a specific channel
   * @param {string} channel - Channel name
   * @param {string} event - Event name
   * @param {Function} callback - Event handler function
   * @returns {Function} - Unsubscribe function
   */
  onChannelEvent(channel, event, callback) {
    if (!this.enableWebSocket || !this.wsManager) {
      console.warn('WebSocket not enabled or manager not available')
      return () => {} // Return no-op unsubscribe function
    }
    
    return this.wsManager.onChannelEvent(channel, event, callback)
  }

  /**
   * Send event to a specific channel
   * @param {string} channel - Channel name
   * @param {string} event - Event name
   * @param {any} data - Event data
   * @returns {boolean} - Success status
   */
  emitToChannel(channel, event, data) {
    if (!this.enableWebSocket || !this.wsManager) {
      console.warn('WebSocket not enabled or manager not available')
      return false
    }
    
    return this.wsManager.emitToChannel(channel, event, data)
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
    if (!this.enableWebSocket || !this.wsManager) {
      console.warn('WebSocket not enabled or manager not available')
      return false
    }
    
    return this.wsManager.sendToRoom(room, event, data)
  }

  /**
   * Get all subscribed channels
   * @returns {Array<string>} - Array of channel names
   */
  getSubscribedChannels() {
    if (!this.enableWebSocket || !this.wsManager) {
      return []
    }
    
    return this.wsManager.getSubscribedChannels()
  }

  /**
   * Check if WebSocket is connected
   * @returns {boolean} - Connection status
   */
  isWebSocketConnected() {
    if (!this.enableWebSocket || !this.wsManager) {
      return false
    }
    
    return this.wsManager.isConnected()
  }

  /**
   * Get WebSocket connection state
   * @returns {string} - Connection state
   */
  getWebSocketConnectionState() {
    if (!this.enableWebSocket || !this.wsManager) {
      return 'disabled'
    }
    
    return this.wsManager.getConnectionState()
  }

  /**
   * Clean up WebSocket resources
   */
  disconnect() {
    if (!this.enableWebSocket || !this.wsManager) {
      return
    }
    
    // Note: We don't disconnect the manager, just leave our channels
    const channels = this.getSubscribedChannels()
    channels.forEach(channel => {
      this.leaveChannel(channel)
    })
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


