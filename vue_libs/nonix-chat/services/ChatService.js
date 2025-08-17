import BaseApiService from '@nonix/services/BaseApiService.js'

export default class ChatService extends BaseApiService {
  // Generic CRUD endpoints for flat data (NO NESTED CRAP!)
  
  // Get all sessions (flat)
  async getSessions() {
    const response = await this.get('/chat-sessions')
    return response
  }

  // Get single session by ID
  async getSession(sessionId) {
    const response = await this.get(`/chat-sessions/${sessionId}`)
    return response
  }

  // Get sessions for specific persona
  async getSessionsByPersona(personaId) {
    const response = await this.get(`/chat-sessions?persona_id=${personaId}`)
    return response
  }

  // Create new session
  async createSession(personaId, sessionName, sessionIcon) {
    const response = await this.post('/chat-sessions', {
      persona_id: personaId,
      session_name: sessionName,
      session_icon: sessionIcon
    })
    return response
  }

  // Get histories for session (flat)
  async getHistories(sessionId) {
    const response = await this.get(`/chat-histories?session_id=${sessionId}`)
    return response
  }

  // Create new history
  async createHistory(sessionId, title) {
    const response = await this.post('/chat-histories', {
      session_id: sessionId,
      title: title
    })
    return response
  }

  // Get messages for history (flat)
  async getHistoryMessages(historyId) {
    // Use the simple ChatMessageService with proper filter format
    const response = await this.get('/chat-messages', { query: { filter_history_id: historyId } })
    return response
  }

  // Send message to history
  async sendMessageToHistory(historyId, content) {
    const response = await this.post('/chat-messages', {
      history_id: historyId,
      role: 'user',
      message_type: 'text',
      content_json: content
    })
    return response
  }

  // Update session (e.g., set current history)
  async updateSession(sessionId, data) {
    const response = await this.put(`/chat-sessions/${sessionId}`, data)
    return response
  }

  // Delete session
  async deleteSession(sessionId) {
    const response = await this.delete(`/chat-sessions/${sessionId}`)
    return response
  }

  // Update history
  async updateHistory(historyId, data) {
    const response = await this.put(`/chat-histories/${historyId}`, data)
    return response
  }

  // Delete history
  async deleteHistory(historyId) {
    const response = await this.delete(`/chat-histories/${historyId}`)
    return response
  }

  // Legacy methods for backward compatibility
  async getPersonas() {
    const response = await this.get('/personas')
    return response
  }

  // Persona tools
  async personaTools(personaId) {
    const response = await this.get(`/chat/personas/${encodeURIComponent(personaId)}/tools`)
    return response
  }

  // MCP status
  async mcpStatus() {
    const response = await this.get('/chat/mcp/servers/status')
    return response
  }
}


