import BaseApiService from '@nonix/services/BaseApiService.js'

export default class ChatService extends BaseApiService {
  // ChatService endpoints for runtime chat operations (NOT CRUD!)
  
  // Session Management
  async getSessions() {
    // Use ChatService endpoint instead of CRUD
    const response = await this.get('/chat/sessions')
    return response.data  // Return extracted data
  }

  async getSession(sessionId) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.get(`/chat/sessions/${sessionId}`)
    return response.data  // Return extracted data
  }

  async createSession(personaId, sessionName, sessionIcon) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.post('/chat/sessions', {
      persona_id: personaId,
      session_name: sessionName,
      session_icon: sessionIcon
    })
    return response.data  // Return extracted data
  }

  async updateSession(sessionId, data) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.put(`/chat/sessions/${sessionId}`, data)
    return response.data  // Return extracted data
  }

  async deleteSession(sessionId) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.delete(`/chat/sessions/${sessionId}`)
    return response.data  // Return extracted data
  }

  // History Management
  async getHistories(sessionId) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.get(`/chat/sessions/${sessionId}/histories`)
    return response.data  // Return extracted data
  }

  async createHistory(sessionId, title) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.post(`/chat/sessions/${sessionId}/histories`, {
      title: title
    })
    return response.data  // Return extracted data
  }

  async updateHistory(sessionId, historyId, data) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.put(`/chat/sessions/${sessionId}/histories/${historyId}`, data)
    return response.data  // Return extracted data
  }

  async deleteHistory(sessionId, historyId) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.delete(`/chat/sessions/${sessionId}/histories/${historyId}`)
    return response.data  // Return extracted data
  }

  // Message Management
  async getHistoryMessages(sessionId, historyId) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.get(`/chat/sessions/${sessionId}/histories/${historyId}/messages`)
    return response.data  // Return extracted data
  }

  async sendMessageToHistory(sessionId, historyId, content) {
    // Use ChatService endpoint instead of CRUD
    const response = await this.post(`/chat/sessions/${sessionId}/histories/${historyId}/send`, {
      content: content
    })
    return response.data  // Return extracted data
  }

  // Persona Management
  async getPersonas() {
    // Use ChatService endpoint (already correct)
    const response = await this.get('/chat/personas')
    return response.data  // Return extracted data
  }

  async getPersonaSessions(personaId) {
    // Use ChatService endpoint (already correct)
    const response = await this.get(`/chat/personas/${personaId}/sessions`)
    return response.data  // Return extracted data
  }

  async startChatWithPersona(personaId, sessionName, sessionIcon) {
    // Use ChatService endpoint (already correct)
    const response = await this.post(`/chat/personas/${personaId}/start-chat`, {
      session_name: sessionName,
      session_icon: sessionIcon
    })
    return response.data  // Return extracted data
  }

  // Tool Management
  async personaTools(personaId) {
    // Use ChatService endpoint (already correct)
    const response = await this.get(`/chat/personas/${personaId}/tools`)
    return response.data  // Return extracted data
  }

  async executeTool(personaId, toolName, toolArgs, historyId, userMessageId) {
    // Use ChatService endpoint (already correct)
    const response = await this.post(`/chat/personas/${personaId}/tools/execute`, {
      tool: toolName,
      args: toolArgs,
      history_id: historyId,
      message_id: userMessageId
    })
    return response.data  // Return extracted data
  }

  // MCP Status
  async mcpStatus() {
    // Use ChatService endpoint (already correct)
    const response = await this.get('/chat/mcp/servers/status')
    return response.data  // Return extracted data
  }

  // Legacy methods for backward compatibility (deprecated - use specific methods above)
  async getSessionsByPersona(personaId) {
    console.warn('getSessionsByPersona is deprecated, use getPersonaSessions instead')
    return this.getPersonaSessions(personaId)
  }

  // Helper method to get session ID from history ID (for backward compatibility)
  async getSessionIdFromHistory(historyId) {
    // Get all sessions and find the one with this history
    const sessionsResponse = await this.getSessions()
    if (sessionsResponse && Array.isArray(sessionsResponse)) {
      for (const session of sessionsResponse) {
        if (session.histories && session.histories.some(h => h.id === historyId)) {
          return session.id
        }
      }
    }
    return null
  }

  // Backward compatibility wrapper for getHistoryMessages with just historyId
  async getHistoryMessagesByHistoryId(historyId) {
    console.warn('getHistoryMessagesByHistoryId is deprecated, use getHistoryMessages(sessionId, historyId) instead')
    const sessionId = await this.getSessionIdFromHistory(historyId)
    if (!sessionId) {
      console.error('No session found for history:', historyId)
      return { data: [] }
    }
    return this.getHistoryMessages(sessionId, historyId)
  }
}


