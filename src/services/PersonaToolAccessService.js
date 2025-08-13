// src/services/PersonaToolAccessService.js
import CrudService from '@/services/CrudService.js'

export default class PersonaToolAccessService extends CrudService {
  constructor() {
    super('persona-tool-access', {
      table: {
        columns: [
          { field: 'persona_id', header: 'Persona', type: 'number', sortable: true },
          { field: 'pattern', header: 'Pattern', type: 'text', sortable: true },
          { field: 'allow', header: 'Allow', type: 'text', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'persona_id', type: 'number', label: 'Persona ID', required: true },
          { key: 'pattern', type: 'text', label: 'Pattern', required: true },
          { key: 'allow', type: 'text', label: 'Allow' }
        ]
      }
    })
  }
}


