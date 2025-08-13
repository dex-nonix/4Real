// src/services/ArtistService.js
import CrudService from '@/services/CrudService.js'

export default class ArtistService extends CrudService {
  constructor() {
    super('artists', {
      table: {
        columns: [
          { field: 'name', header: 'Artist Name', type: 'text', sortable: true },
          { field: 'abbreviation', header: 'Abbr', type: 'text', sortable: true }
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
          { key: 'name', type: 'text', label: 'Artist Name', required: true, props: { placeholder: 'Enter artist name' } },
          { key: 'abbreviation', type: 'text', label: 'Abbreviation', required: true, props: { placeholder: 'Enter abbreviation' } }
        ]
      }
    })
  }
}


