// src/services/AIProviderService.js
import CrudService from '@/services/CrudService.js'

export default class AIProviderService extends CrudService {
  constructor() {
    super('ai-providers', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'provider_type', header: 'Type', type: 'text', sortable: true },
          { field: 'module', header: 'Module', type: 'text', sortable: true },
          { field: 'cls', header: 'Class', type: 'text', sortable: true },
          { field: 'method', header: 'Method', type: 'text', sortable: true },
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
          { key: 'name', type: 'text', label: 'Name', required: true },
          { key: 'provider_type', type: 'text', label: 'Type', required: true },
          { key: 'module', type: 'text', label: 'Module', required: true },
          { key: 'cls', type: 'text', label: 'Class', required: true },
          { key: 'method', type: 'text', label: 'Method (default: invoke)' },
          { key: 'config_json', type: 'json', label: 'Config (JSON)' },
          { key: 'is_active', type: 'boolean', label: 'Active' }
        ]
      }
    })
  }
}


