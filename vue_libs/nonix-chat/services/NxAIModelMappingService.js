import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class NxAIModelMappingService extends NxCrudService {
  constructor(app) {
    super(app,'ai-model-mappings', {
      table: {
        columns: [
          { field: 'provider_id', header: 'Provider', type: 'fk_display', sortable: true, props: { entity: 'ai-providers' } },
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'model_name', header: 'Model', type: 'text', sortable: true },
          { field: 'is_active', header: 'Active', type: 'boolean', sortable: true }
        ],
        actions: ['view', 'edit', 'delete'],
        bulkActions: ['delete', 'export'],
        filters: ['search'],
        paginated: true,
        pageSize: 20,
        selectionMode: 'multiple',
        resizable: true,
        striped: true,
        hover: true
      },
      form: {
        fields: [
          { key: 'provider_id', type: 'fk_select', label: 'Provider', required: true, props: { entity: 'ai-providers', search: true } },
          { key: 'name', type: 'text', label: 'Name', required: true },
          { key: 'model_name', type: 'text', label: 'Model Name', required: true },
          { key: 'parameters_json', type: 'json', label: 'Parameters (JSON)' },
          { key: 'is_active', type: 'boolean', label: 'Active' }
        ]
      }
    })
  }
}


