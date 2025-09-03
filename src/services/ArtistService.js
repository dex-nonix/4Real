// src/services/ArtistService.js
import CrudService from '@/services/CrudService.js'

export default class ArtistService extends CrudService {
  constructor(app) {
    super(app,'artists', {
      table: {
        columns: [
          { field: 'name', header: 'Artist Name', type: 'text', sortable: true },
          { field: 'abbreviation', header: 'Abbr', type: 'text', sortable: true },
          { field: 'persona', header: 'Persona', type: 'text', sortable: false },
          { field: 'birth_date', header: 'Birth Date', type: 'date', sortable: true }
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
          { key: 'abbreviation', type: 'text', label: 'Abbreviation', required: true, props: { placeholder: 'Enter abbreviation' } },
          { key: 'persona', type: 'textarea', label: 'Persona', required: false, props: { placeholder: 'Enter artist persona/description' } },
          { key: 'birth_date', type: 'date', label: 'Birth Date', required: false, props: { placeholder: 'Select birth date' } }
        ]
      }
    })
  }
}


