import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class NxMCPServerService extends NxCrudService {
  constructor(app) {
    super(app,'mcp-servers', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'transport', header: 'Transport', type: 'text', sortable: true },
          { field: 'command', header: 'Command/URL', type: 'mcp_connection', sortable: false },
          { field: 'is_active', header: 'Active', type: 'boolean', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'name', type: 'text', label: 'Name', required: true },
          { key: 'transport', type: 'select', label: 'Transport', options: [
            { label: 'Stdio (Local)', value: 'stdio' },
            { label: 'WebSocket', value: 'websocket' },
            { label: 'HTTP', value: 'http' },
            { label: 'Streamable Http', value: 'streamable_http' }
          ]},
          { key: 'command', type: 'text', label: 'Command', required: false, check: (formData) => {
            const transport = formData.transport || 'stdio'
            return transport === 'stdio'
          }},
          { key: 'url', type: 'text', label: 'URL', required: false, check: (formData) => {
            const transport = formData.transport || 'stdio'
            return transport === 'websocket' || transport === 'http' || transport === 'streamable_http'
          }},
          { key: 'args_json', type: 'json', label: 'Args (JSON array)' },
          { key: 'env_json', type: 'json', label: 'Env (JSON obj)' },
          { key: 'is_active', type: 'boolean', label: 'Active' }
        ]
      }
    })
  }
}


