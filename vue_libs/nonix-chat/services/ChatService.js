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

  async sendMessage(sessionId, historyId, content) {
    // historyId is MANDATORY parameter
    let url;
    if (historyId) {
        // Specific history
        url = `/chat/sessions/${sessionId}/histories/${historyId}/send`;
    } else {
        // Current history (extracted by backend)
        url = `/chat/sessions/${sessionId}/send`;
    }

    const response = await this.post(url, { content: content });
    return response.data;
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

  // MCP Status
  async mcpStatus() {

    const response = await this.get('/chat/mcp/servers/status')
    return response.data
  }

}


