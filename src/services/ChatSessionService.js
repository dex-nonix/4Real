// src/services/ChatSessionService.js
import CrudService from '@/services/CrudService.js'

export default class ChatSessionService extends CrudService {
  constructor(app) {
    super(app,'chat-sessions', {
      table: {
        columns: [
          { field: 'title', header: 'Title', type: 'text', sortable: true },
          { field: 'persona_id', header: 'Persona', type: 'fk_display', sortable: true, props: { entity: 'personas' } },
          { field: 'created_by', header: 'Created By', type: 'text', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'persona_id', type: 'fk_select', label: 'Persona', required: true, props: { entity: 'personas', search: true } },
          { key: 'title', type: 'text', label: 'Title', required: true },
          { key: 'created_by', type: 'text', label: 'Created By' },
          { key: 'metadata_json', type: 'json', label: 'Metadata (JSON)' }
        ]
      }
    })
  }
}


