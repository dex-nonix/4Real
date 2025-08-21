// src/services/AlbumService.js
import CrudService from '@/services/CrudService.js'

export default class AlbumService extends CrudService {
  constructor(app) {
    super(app, 'albums', {
      table: {
        columns: [
          { field: 'title', header: 'Title', type: 'text', sortable: true },
          { field: 'artist_id', header: 'Artist', type: 'fk_display', sortable: true, props: { entity: 'artists' } },
          { field: 'release_date', header: 'Release Date', type: 'date', sortable: true }
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
          { key: 'artist_id', type: 'fk_select', label: 'Artist', required: true, props: { entity: 'artists', search: true } },
          { key: 'title', type: 'text', label: 'Title', required: true, props: { placeholder: 'Enter album title' } },
          { key: 'release_date', type: 'date', label: 'Release Date', props: { dateFormat: 'yy-mm-dd' } },
          { key: 'description', type: 'text', label: 'Description', props: { placeholder: 'Enter description' } }
        ]
      }
    })
  }
}


