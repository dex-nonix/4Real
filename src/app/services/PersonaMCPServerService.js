// src/services/PersonaMCPServerService.js
import CrudService from '@/app/services/CrudService.js'

export default class PersonaMCPServerService extends CrudService {
  constructor() {
    super('persona-mcp-servers', {
      table: {
        columns: [
          { field: 'persona_id', header: 'Persona', type: 'fk_display', sortable: true, props: { entity: 'personas' } },
          { field: 'mcp_server_id', header: 'MCP Server', type: 'fk_display', sortable: true, props: { entity: 'mcp-servers' } },
          { field: 'is_active', header: 'Active', type: 'boolean', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'persona_id', type: 'fk_select', label: 'Persona', required: true, props: { entity: 'personas', search: true } },
          { key: 'mcp_server_id', type: 'fk_select', label: 'MCP Server', required: true, props: { entity: 'mcp-servers', search: true } },
          { key: 'override_args_json', type: 'json', label: 'Override Args (JSON array)' },
          { key: 'override_env_json', type: 'json', label: 'Override Env (JSON obj)' },
          { key: 'is_active', type: 'boolean', label: 'Active' }
        ]
      }
    })
  }
}


