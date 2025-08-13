// src/services/AIModelMappingService.js
import CrudService from '@/services/CrudService.js'

export default class AIModelMappingService extends CrudService {
  constructor() {
    super('ai-model-mappings', {
      table: {
        columns: [
          { field: 'provider_id', header: 'Provider ID', type: 'text', sortable: true },
          { field: 'purpose', header: 'Purpose', type: 'text', sortable: true },
          { field: 'model_name', header: 'Model', type: 'text', sortable: true },
          { field: 'is_active', header: 'Active', type: 'text', sortable: true }
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
          { key: 'provider_id', type: 'text', label: 'Provider ID', required: true },
          { key: 'purpose', type: 'text', label: 'Purpose', required: true },
          { key: 'model_name', type: 'text', label: 'Model Name', required: true },
          { key: 'parameters_json', type: 'json', label: 'Parameters (JSON)' },
          { key: 'is_active', type: 'text', label: 'Active' }
        ]
      }
    })
  }
}


