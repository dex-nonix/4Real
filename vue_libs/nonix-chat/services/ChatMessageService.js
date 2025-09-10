import CrudService from '@/services/CrudService.js'

export default class ChatMessageService extends CrudService {
  constructor(app) {
    super(app,'chat-messages', {
      table: {
        columns: [
          { field: 'history_id', header: 'History', type: 'fk_display', sortable: true, props: { entity: 'chat-histories' } },
          { field: 'role', header: 'Role', type: 'text', sortable: true },
          { field: 'message_type', header: 'Type', type: 'text', sortable: true },
          { field: 'status', header: 'Status', type: 'text', sortable: true },
          { field: 'seq', header: 'Sequence', type: 'number', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'history_id', type: 'fk_select', label: 'History', required: true, props: { entity: 'chat-histories', search: true } },
          { key: 'role', type: 'text', label: 'Role', required: true },
          { key: 'message_type', type: 'text', label: 'Message Type', required: true },
          { key: 'content_json', type: 'json', label: 'Content (JSON)' },
          { key: 'status', type: 'text', label: 'Status', required: true },
          { key: 'seq', type: 'number', label: 'Sequence' },
          { key: 'turn_id', type: 'text', label: 'Turn ID' },
          { key: 'run_id', type: 'text', label: 'Run ID' },
          { key: 'parent_ids', type: 'json', label: 'Parent IDs (JSON)' },
          { key: 'tool_run_id', type: 'text', label: 'Tool Run ID' }
        ]
      }
    })
  }
}


