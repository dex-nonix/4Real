// src/services/ChatMessageService.js
import CrudService from '@/services/CrudService.js'

export default class ChatMessageService extends CrudService {
  constructor(app) {
    super(app,'chat-messages', {
      table: {
        columns: [
          { field: 'session_id', header: 'Session', type: 'number', sortable: true },
          { field: 'role', header: 'Role', type: 'text', sortable: true },
          { field: 'created_at', header: 'Created', type: 'text', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'session_id', type: 'number', label: 'Session ID', required: true },
          { key: 'role', type: 'text', label: 'Role', required: true },
          { key: 'content_json', type: 'json', label: 'Content (JSON)' }
        ]
      }
    })
  }
}


