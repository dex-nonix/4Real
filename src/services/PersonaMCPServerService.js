// src/services/PersonaMCPServerService.js
import CrudService from '@/services/CrudService.js'

export default class PersonaMCPServerService extends CrudService {
  constructor() {
    super('persona-mcp-servers', {
      table: {
        columns: [
          { field: 'persona_id', header: 'Persona', type: 'number', sortable: true },
          { field: 'mcp_server_id', header: 'MCP Server', type: 'number', sortable: true },
          { field: 'is_active', header: 'Active', type: 'text', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'persona_id', type: 'number', label: 'Persona ID', required: true },
          { key: 'mcp_server_id', type: 'number', label: 'MCP Server ID', required: true },
          { key: 'override_args_json', type: 'json', label: 'Override Args (JSON array)' },
          { key: 'override_env_json', type: 'json', label: 'Override Env (JSON obj)' },
          { key: 'is_active', type: 'text', label: 'Active' }
        ]
      }
    })
  }
}


