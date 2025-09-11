import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class NxInternalToolService extends NxCrudService {
  constructor(app) {
    super(app,'internal-tools', {
      table: {
        columns: [
          { field: 'qualified_name', header: 'Qualified Name', type: 'text', sortable: true },
          { field: 'namespace', header: 'Namespace', type: 'text', sortable: true },
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'is_active', header: 'Active', type: 'boolean', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'namespace', type: 'text', label: 'Namespace', required: true },
          { key: 'name', type: 'text', label: 'Name', required: true },
          { key: 'qualified_name', type: 'text', label: 'Qualified Name', required: true },
          { key: 'description', type: 'textarea', label: 'Description' },
          { key: 'config_json', type: 'json', label: 'Config (JSON)' },
          { key: 'is_active', type: 'boolean', label: 'Active' }
        ]
      }
    })
  }
}


