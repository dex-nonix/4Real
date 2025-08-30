// src/services/PersonaToolAccessService.js
import CrudService from '@/services/CrudService.js'

export default class PersonaToolAccessService extends CrudService {
  constructor(app) {
    super(app,'persona-tool-access', {
      table: {
        columns: [
          { field: 'persona_id', header: 'Persona', type: 'fk_display', sortable: true, props: { entity: 'personas' } },
          { field: 'pattern', header: 'Pattern', type: 'text', sortable: true },
          { field: 'allow', header: 'Allow', type: 'boolean', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'persona_id', type: 'fk_select', label: 'Persona', required: true, props: { entity: 'personas', search: true } },
          { key: 'pattern', type: 'llm_tool', label: 'Tool', required: true, props: { allowWildcards: true } },
          { key: 'allow', type: 'boolean', label: 'Allow' }
        ]
      }
    })
  }
}


