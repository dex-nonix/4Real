// BaseApiService.js - minimal fetch-based HTTP layer

export default class BaseApiService {
  constructor(options = {}) {
    const { baseURL, defaultHeaders = {}, onRequest, onResponse, onError, fetchImpl } = options
    if (typeof baseURL !== 'string') {
      throw new Error('BaseApiService requires a baseURL string')
    }
    this.baseURL = baseURL.replace(/\/$/, '')
    this.defaultHeaders = { 'Content-Type': 'application/json', ...defaultHeaders }
    this.onRequest = onRequest
    this.onResponse = onResponse
    this.onError = onError
    this.fetchImpl = fetchImpl || fetch
    this.authToken = null
  }

  setAuthToken(token) {
    this.authToken = token || null
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
    const url = this.buildUrl(path, query)
    const finalHeaders = { ...this.defaultHeaders, ...headers }
    if (this.authToken) {
      finalHeaders['Authorization'] = `Bearer ${this.authToken}`
    }

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
      const res = await this.fetchImpl(url, init)
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


