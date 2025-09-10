import CrudService from '@/services/CrudService.js'

export default class ChatHistoryService extends CrudService {
  constructor(app) {
    super(app,'chat-histories', {
      table: {
        columns: [
          { field: 'session_id', header: 'Session', type: 'fk_display', sortable: true, props: { entity: 'chat-sessions' } },
          { field: 'title', header: 'Title', type: 'text', sortable: true },
          { field: 'summary', header: 'Summary', type: 'text', sortable: true },
          { field: 'message_count', header: 'Messages', type: 'number', sortable: true },
          { field: 'created_at', header: 'Created', type: 'date', sortable: true }
        ],
        actions: ['view', 'edit', 'delete'],
        bulkActions: ['delete', 'export'],
        filters: ['search', 'date_range'],
        paginated: true,
        pageSize: 20,
        selectionMode: 'multiple',
        resizable: true,
        striped: true,
        hover: true
      },
      form: {
        fields: [
          { key: 'session_id', type: 'fk_select', label: 'Session', required: true, props: { entity: 'chat-sessions', search: true } },
          { key: 'title', type: 'text', label: 'Title', required: true, props: { placeholder: 'Enter history title' } },
          { key: 'summary', type: 'textarea', label: 'Summary', required: false, props: { placeholder: 'Enter summary' } },
          { key: 'message_count', type: 'number', label: 'Message Count', required: false, props: { placeholder: '0' } }
        ]
      }
    })
  }
}
