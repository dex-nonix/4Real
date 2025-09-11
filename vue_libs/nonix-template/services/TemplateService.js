// src/services/TemplateService.js
import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class TemplateService extends NxCrudService {
  constructor(app) {
    super(app,'templates', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'description', header: 'Description', type: 'text', sortable: true },
          { field: 'content', header: 'Content', type: 'text', sortable: false },
          { field: 'parent_template_id', header: 'Parent Template', type: 'fk_display', sortable: true, props: { entity: 'templates' } },
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
          { key: 'name', type: 'text', label: 'Name', required: true, props: { placeholder: 'Enter template name' } },
          { key: 'description', type: 'textarea', label: 'Description', required: false, props: { placeholder: 'Enter template description' } },
          { key: 'content', type: 'textarea', label: 'Content', required: true, props: { placeholder: 'Enter template content' } },
          { key: 'context', type: 'json', label: 'Context (JSON)', required: false },
          { key: 'parent_template_id', type: 'fk_select', label: 'Parent Template', required: false, props: { entity: 'templates', search: true, placeholder: 'Select a parent template (optional)' } }
        ]
      }
    })
  }
}
