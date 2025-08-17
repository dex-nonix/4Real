import BaseApiService from '@nonix/services/BaseApiService.js'

export default class ChatRuntimeService extends BaseApiService {
  // Get all personas with their sessions
  getPersonas() {
    return this.get('/chat/personas')
  }

  // Get all sessions for a specific persona
  getSessions(personaId) {
    return this.get(`/chat/personas/${encodeURIComponent(personaId)}/sessions`)
  }

  // Create new session with persona
  createSession(personaId, sessionName, sessionIcon) {
    return this.post(`/chat/personas/${encodeURIComponent(personaId)}/start-chat`, {
      session_name: sessionName,
      session_icon: sessionIcon
    })
  }

  // Get histories within a session
  getHistories(sessionId) {
    return this.get(`/chat-histories?session_id=${encodeURIComponent(sessionId)}`)
  }

  // Create new history within session
  createHistory(sessionId, title) {
    return this.post(`/chat-histories`, {
      session_id: sessionId,
      title: title
    })
  }

  // Get messages from specific history
  getHistoryMessages(sessionId, historyId) {
    return this.get(`/chat-messages?history_id=${encodeURIComponent(historyId)}`)
  }

  // Send message to specific history
  sendMessageToHistory(sessionId, historyId, content) {
    return this.post(`/chat-messages`, {
      history_id: historyId,
      role: 'user',
      message_type: 'text',
      content_json: content
    })
  }

  // Activate a different history
  activateHistory(sessionId, historyId) {
    return this.put(`/chat-sessions/${encodeURIComponent(sessionId)}`, {
      current_history_id: historyId
    })
  }

  // Update history (rename)
  updateHistory(sessionId, historyId, title, summary) {
    return this.put(`/chat-histories/${encodeURIComponent(historyId)}`, {
      title: title,
      summary: summary
    })
  }

  // Delete history
  deleteHistory(sessionId, historyId) {
    return this.delete(`/chat-histories/${encodeURIComponent(historyId)}`)
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
    return this.get(`/chat/personas/${encodeURIComponent(personaId)}/tools`)
  }

  // MCP status
  mcpStatus() {
    return this.get('/chat/mcp/servers/status')
  }
}


