// src/services/StyleService.js
import CrudService from '@/services/CrudService.js'

export default class StyleService extends CrudService {
  constructor(app) {
    super(app,'styles', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'description', header: 'Description', type: 'text' }
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
          { key: 'name', type: 'text', label: 'Name', required: true, props: { placeholder: 'Enter style name' } },
          { key: 'description', type: 'text', label: 'Description' }
        ]
      }
    })
  }
}


