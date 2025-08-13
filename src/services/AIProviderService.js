// src/services/AIProviderService.js
import CrudService from '@/services/CrudService.js'

export default class AIProviderService extends CrudService {
  constructor() {
    super('ai-providers', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'provider_type', header: 'Type', type: 'text', sortable: true },
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
          { key: 'name', type: 'text', label: 'Name', required: true },
          { key: 'provider_type', type: 'text', label: 'Type', required: true },
          { key: 'config_json', type: 'json', label: 'Config (JSON)' },
          { key: 'is_active', type: 'text', label: 'Active' }
        ]
      }
    })
  }
}


