import CrudService from '@/services/CrudService.js'

export default class ToolInvocationLogService extends CrudService {
  constructor(app) {
    super(app,'tool-invocation-logs', {
      table: {
        columns: [
          { field: 'history_id', header: 'History', type: 'fk_display', sortable: true, props: { entity: 'chat-histories' } },
          { field: 'message_id', header: 'Message', type: 'fk_display', sortable: true, props: { entity: 'chat-messages' } },
          { field: 'tool_name', header: 'Tool', type: 'text', sortable: true },
          { field: 'status', header: 'Status', type: 'text', sortable: true },
          { field: 'duration_ms', header: 'Duration (ms)', type: 'number', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'history_id', type: 'fk_select', label: 'History', required: true, props: { entity: 'chat-histories', search: true } },
          { key: 'message_id', type: 'fk_select', label: 'Message', required: true, props: { entity: 'chat-messages', search: true } },
          { key: 'tool_name', type: 'text', label: 'Tool Name', required: true },
          { key: 'status', type: 'text', label: 'Status', required: true },
          { key: 'input_json', type: 'json', label: 'Input (JSON)' },
          { key: 'output_json', type: 'json', label: 'Output (JSON)' },
          { key: 'duration_ms', type: 'number', label: 'Duration (ms)' },
          { key: 'seq', type: 'number', label: 'Sequence', required: true },
          { key: 'turn_id', type: 'text', label: 'Turn ID', required: true },
          { key: 'run_id', type: 'text', label: 'Run ID' },
          { key: 'parent_ids', type: 'json', label: 'Parent IDs (JSON)' },
          { key: 'tool_run_id', type: 'text', label: 'Tool Run ID', required: true }
        ]
      }
    })
  }
}


