// src/services/RhymeTechniqueService.js
import NxCrudService from '@/services/NxCrudService.js'

export default class RhymeTechniqueService extends NxCrudService {
  constructor(app) {
    super(app,'rhyme-techniques', {
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
          { key: 'name', type: 'text', label: 'Name', required: true, props: { placeholder: 'Enter technique name' } },
          { key: 'description', type: 'text', label: 'Description' }
        ]
      }
    })
  }
}


