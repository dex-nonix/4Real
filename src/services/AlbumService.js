// src/services/AlbumService.js
import CrudService from '@/services/CrudService.js'

export default class AlbumService extends CrudService {
  constructor() {
    super('albums', {
      table: {
        columns: [
          { field: 'title', header: 'Title', type: 'text', sortable: true },
          { field: 'artist_id', header: 'Artist ID', type: 'text', sortable: true },
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
          { key: 'artist_id', type: 'text', label: 'Artist ID', required: true, props: { placeholder: 'Enter artist ID' } },
          { key: 'title', type: 'text', label: 'Title', required: true, props: { placeholder: 'Enter album title' } },
          { key: 'release_date', type: 'date', label: 'Release Date', props: { dateFormat: 'yy-mm-dd' } },
          { key: 'description', type: 'text', label: 'Description', props: { placeholder: 'Enter description' } }
        ]
      }
    })
  }
}


