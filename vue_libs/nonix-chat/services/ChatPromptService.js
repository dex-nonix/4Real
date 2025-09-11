import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class ChatPromptService extends NxCrudService {
  constructor(app) {
    super(app,'chat-prompts', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'description', header: 'Description', type: 'text', sortable: true },
          { field: 'template_id', header: 'Template', type: 'fk_display', sortable: true, props: { entity: 'templates' } },
          { field: 'content', header: 'Content', type: 'text', sortable: false },
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
          { key: 'name', type: 'text', label: 'Name', required: true, props: { placeholder: 'Enter chat prompt name' } },
          { key: 'description', type: 'textarea', label: 'Description', required: false, props: { placeholder: 'Enter chat prompt description' } },
          { key: 'template_id', type: 'fk_select', label: 'Template', required: false, props: { entity: 'templates', search: true, placeholder: 'Select a template (optional)' } },
          { key: 'content', type: 'textarea', label: 'Content', required: false, props: { placeholder: 'Enter prompt content' } },
          { key: 'context', type: 'json', label: 'Context (JSON)', required: false }
        ]
      }
    })
  }
}
