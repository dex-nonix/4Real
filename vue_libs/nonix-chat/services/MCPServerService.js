import NxCrudService from '@/services/NxCrudService.js'

export default class MCPServerService extends NxCrudService {
  constructor(app) {
    super(app,'mcp-servers', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'command', header: 'Command', type: 'text', sortable: true },
          { field: 'is_active', header: 'Active', type: 'boolean', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'name', type: 'text', label: 'Name', required: true },
          { key: 'command', type: 'text', label: 'Command', required: true },
          { key: 'args_json', type: 'json', label: 'Args (JSON array)' },
          { key: 'env_json', type: 'json', label: 'Env (JSON obj)' },
          { key: 'is_active', type: 'boolean', label: 'Active' }
        ]
      }
    })
  }
}


