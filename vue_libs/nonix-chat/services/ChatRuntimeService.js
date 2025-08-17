import BaseApiService from '@nonix/services/BaseApiService.js'

export default class ChatRuntimeService extends BaseApiService {
  basePath() { return '/chat' }

  // Get all personas with their sessions
  getPersonas() {
    return this.get('/personas')
  }

  // Get all sessions for a specific persona
  getSessions(personaId) {
    return this.get(`/personas/${encodeURIComponent(personaId)}/sessions`)
  }

  // Create new session with persona
  createSession(personaId, sessionName, sessionIcon) {
    return this.post(`/personas/${encodeURIComponent(personaId)}/start-chat`, {
      session_name: sessionName,
      session_icon: sessionIcon
    })
  }

  // Get histories within a session
  getHistories(sessionId) {
    return this.get(`/chat-sessions/${encodeURIComponent(sessionId)}/histories`)
  }

  // Create new history within session
  createHistory(sessionId, title) {
    return this.post(`/chat-sessions/${encodeURIComponent(sessionId)}/histories`, {
      title: title
    })
  }

  // Get messages from specific history
  getHistoryMessages(sessionId, historyId) {
    return this.get(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}/messages`)
  }

  // Send message to specific history
  sendMessageToHistory(sessionId, historyId, content) {
    return this.post(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}/send`, {
      content: content
    })
  }

  // Activate a different history
  activateHistory(sessionId, historyId) {
    return this.post(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}/activate`)
  }

  // Update history (rename)
  updateHistory(sessionId, historyId, title, summary) {
    return this.put(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}`, {
      title: title,
      summary: summary
    })
  }

  // Delete history
  deleteHistory(sessionId, historyId) {
    return this.delete(`/chat-sessions/${encodeURIComponent(sessionId)}/histories/${encodeURIComponent(historyId)}`)
  }

  // Legacy methods (keep for compatibility)
  listSessions(params = {}) {
    return this.get('/chat-sessions', { query: params })
  }

  getSession(id) {
    return this.get(`/chat-sessions/${encodeURIComponent(id)}`)
  }

  send(sessionId, content) {
    return this.post(`/chat-sessions/${encodeURIComponent(sessionId)}/send`, { content })
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


