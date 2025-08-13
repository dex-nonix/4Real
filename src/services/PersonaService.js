// src/services/PersonaService.js
import CrudService from '@/services/CrudService.js'

export default class PersonaService extends CrudService {
  constructor() {
    super('personas', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'is_active', header: 'Active', type: 'text', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'name', type: 'text', label: 'Name', required: true },
          { key: 'is_active', type: 'text', label: 'Active' },
          { key: 'system_prompt', type: 'textarea', label: 'System Prompt' },
          { key: 'metadata_json', type: 'json', label: 'Metadata (JSON)' }
        ]
      }
    })
  }
}


