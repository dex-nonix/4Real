// src/services/ToolInvocationLogService.js
import CrudService from '@/app/services/CrudService.js'

export default class ToolInvocationLogService extends CrudService {
  constructor() {
    super('tool-invocation-logs', {
      table: {
        columns: [
          { field: 'session_id', header: 'Session', type: 'number', sortable: true },
          { field: 'tool_name', header: 'Tool', type: 'text', sortable: true },
          { field: 'status', header: 'Status', type: 'text', sortable: true },
          { field: 'duration_ms', header: 'Duration (ms)', type: 'number', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'session_id', type: 'number', label: 'Session ID', required: true },
          { key: 'message_id', type: 'number', label: 'Message ID' },
          { key: 'tool_name', type: 'text', label: 'Tool Name', required: true },
          { key: 'status', type: 'text', label: 'Status', required: true },
          { key: 'input_json', type: 'json', label: 'Input (JSON)' },
          { key: 'output_json', type: 'json', label: 'Output (JSON)' },
          { key: 'duration_ms', type: 'number', label: 'Duration (ms)' }
        ]
      }
    })
  }
}


