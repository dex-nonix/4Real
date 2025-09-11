// NxBaseApiService.js - minimal fetch-based HTTP layer with WebSocket support
import { API_BASE_URL } from '@/env.js'

export default class NxBaseApiService {
  constructor(app, options = {}) {
    const { defaultHeaders = {}, onRequest, onResponse, onError} = options
    this.baseURL = API_BASE_URL.replace(/\/$/, '')
    this.defaultHeaders = { 'Content-Type': 'application/json', ...defaultHeaders }
    this.onRequest = onRequest
    this.onResponse = onResponse
    this.onError = onError
    this.wsManager = app._context.provides['websocket-manager'];
  }


  /**
   * Join a specific WebSocket room
   * @param {string} room - Room name (e.g., 'chat/123/456')
   * @returns {boolean} - Success status
   */
  joinRoom(room) {
    return this.wsManager.joinRoom(room)
  }

  /**
   * Leave a specific WebSocket room
   * @param {string} room - Room name to leave
   * @returns {boolean} - Success status
   */
  leaveRoom(room) {
    return this.wsManager.leaveRoom(room)
  }

  /**
   * Listen to WebSocket events
   * @param {string} event - Event name
   * @param {Function} callback - Event handler function
   * @returns {Function} - Unsubscribe function
   */
  onWebSocketEvent(event, callback) {
    return this.wsManager.on(event, callback)
  }

  /**
   * Emit WebSocket event
   * @param {string} event - Event name
   * @param {any} data - Event data
   * @returns {boolean} - Success status
   */
  emitWebSocketEvent(event, data) {
    return this.wsManager.emit(event, data)
  }

  /**
   * Emit WebSocket event to a specific room
   * @param {string} room - Room name
   * @param {string} event - Event name
   * @param {any} data - Event data
   * @returns {boolean} - Success status
   */
  emitWebSocketEventToRoom(room, event, data) {
    return this.wsManager.emitToRoom(room, event, data)
  }

  /**
   * Check if WebSocket is connected
   * @returns {boolean} - Connection status
   */
  isWebSocketConnected() {
    return this.wsManager.isConnected()
  }

  /**
   * Get WebSocket connection state
   * @returns {string} - Connection state
   */
  getWebSocketConnectionState() {
    return this.wsManager.getConnectionState()
  }

  /**
   * Clean up WebSocket resources
   */
  disconnect() {
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


