import BaseApiService from '@nonix/services/BaseApiService.js'

export default class ChatService extends BaseApiService {
  
  async getSessions() {
    
    const response = await this.get('/chat/sessions')
    return response.data  
  }

  async getSession(sessionId) {
    
    const response = await this.get(`/chat/sessions/${sessionId}`)
    return response.data  
  }

  async createSession(personaId, sessionName, sessionIcon) {
    
    const response = await this.post('/chat/sessions', {
      persona_id: personaId,
      session_name: sessionName,
      session_icon: sessionIcon
    })
    return response.data  
  }

  async updateSession(sessionId, data) {
    
    const response = await this.put(`/chat/sessions/${sessionId}`, data)
    return response.data  
  }

  async deleteSession(sessionId) {
    
    const response = await this.delete(`/chat/sessions/${sessionId}`)
    return response.data  
  }

  // History Management
  async getHistories(sessionId) {
    
    const response = await this.get(`/chat/sessions/${sessionId}/histories`)
    return response.data  
  }

  async createHistory(sessionId, title) {
    
    const response = await this.post(`/chat/sessions/${sessionId}/histories`, {
      title: title
    })
    return response.data  
  }

  async updateHistory(sessionId, historyId, data) {
    
    const response = await this.put(`/chat/sessions/${sessionId}/histories/${historyId}`, data)
    return response.data  
  }

  async deleteHistory(sessionId, historyId) {
    const response = await this.delete(`/chat/sessions/${sessionId}/histories/${historyId}`)
    return response.data  
  }

  // Message Management
  async getHistoryMessages(sessionId, historyId) {
    const response = await this.get(`/chat/sessions/${sessionId}/histories/${historyId}/messages`)
    return response.data  
  }

  async clearHistoryMessages(sessionId, historyId) {
    const response = await this.delete(`/chat/sessions/${sessionId}/histories/${historyId}/messages`)
    return response.data  
  }

  async deleteMessage(sessionId, historyId, messageId) {
    const response = await this.delete(`/chat/sessions/${sessionId}/histories/${historyId}/messages/${messageId}`)
    return response.data  
  }

  async sendMessageToHistory(sessionId, historyId, content) {
    const response = await this.post(`/chat/sessions/${sessionId}/send`, {
      content: content
    })
    return response.data  
  }

  // Persona Management
  async getPersonas() {
    
    const response = await this.get('/chat/personas')
    return response.data  
  }

  async getPersona(personaId) {
    const response = await this.get(`/chat/personas/${personaId}`)
    return response.data  
  }

  async getPersonaSessions(personaId) {
    
    const response = await this.get(`/chat/personas/${personaId}/sessions`)
    return response.data  
  }

  async startChatWithPersona(personaId, sessionName, sessionIcon) {
    
    const response = await this.post(`/chat/personas/${personaId}/start-chat`, {
      session_name: sessionName,
      session_icon: sessionIcon
    })
    return response.data  
  }

  // Tool Management
  async personaTools(personaId) {
    
    const response = await this.get(`/chat/personas/${personaId}/tools`)
    return response.data  
  }

  async executeTool(personaId, toolName, toolArgs, historyId, userMessageId) {
    
    const response = await this.post(`/chat/personas/${personaId}/tools/execute`, {
      tool_name: toolName,
      args: toolArgs,
      history_id: historyId,
      message_id: userMessageId
    })
    return response.data  
  }

  // MCP Status
  async mcpStatus() {
    
    const response = await this.get('/chat/mcp/servers/status')
    return response.data  
  }


  async getSessionIdFromHistory(historyId) {    
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

}


