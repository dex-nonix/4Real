// src/services/ChatSessionService.js
import CrudService from '@/services/CrudService.js'

export default class ChatSessionService extends CrudService {
  constructor() {
    super('chat-sessions', {
      table: {
        columns: [
          { field: 'title', header: 'Title', type: 'text', sortable: true },
          { field: 'persona_id', header: 'Persona', type: 'number', sortable: true },
          { field: 'created_by', header: 'Created By', type: 'text', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'persona_id', type: 'number', label: 'Persona ID', required: true },
          { key: 'title', type: 'text', label: 'Title', required: true },
          { key: 'created_by', type: 'text', label: 'Created By' },
          { key: 'metadata_json', type: 'json', label: 'Metadata (JSON)' }
        ]
      }
    })
  }
}


