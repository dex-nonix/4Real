// src/services/ChatRuntimeService.js
import BaseApiService from '@/services/BaseApiService.js'

export default class ChatRuntimeService extends BaseApiService {
  basePath() { return '/chat' }

  // Sessions
  createSession(payload) {
    // payload: { persona_id, title?, created_by?, metadata? }
    return this.post('/sessions', payload)
  }

  listSessions(params = {}) {
    return this.get('/sessions', { query: params })
  }

  getSession(id) {
    return this.get(`/sessions/${encodeURIComponent(id)}`)
  }

  // Messages
  listMessages(sessionId) {
    return this.get(`/sessions/${encodeURIComponent(sessionId)}/messages`)
  }

  send(sessionId, content) {
    return this.post(`/sessions/${encodeURIComponent(sessionId)}/send`, { content })
  }

  retry(sessionId) {
    return this.post(`/sessions/${encodeURIComponent(sessionId)}/retry`, {})
  }

  // Persona tools
  personaTools(personaId) {
    return this.get(`/personas/${encodeURIComponent(personaId)}/tools`)
  }

  // MCP status
  mcpStatus() {
    return this.get('/mcp/servers/status')
  }
}


