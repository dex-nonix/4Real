// src/services/TrackService.js
import CrudService from '@/services/CrudService.js'

export default class TrackService extends CrudService {
  constructor() {
    super('tracks', {
      table: {
        columns: [
          { field: 'title', header: 'Title', type: 'text', sortable: true },
          { field: 'album_id', header: 'Album', type: 'fk_display', sortable: true, props: { entity: 'albums' } },
          { field: 'track_number', header: 'Track #', type: 'number', sortable: true },
          { field: 'duration_seconds', header: 'Duration (s)', type: 'number', sortable: true }
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
          { key: 'album_id', type: 'fk_select', label: 'Album', required: true, props: { entity: 'albums', search: true } },
          { key: 'title', type: 'text', label: 'Title', required: true, props: { placeholder: 'Enter track title' } },
          { key: 'track_number', type: 'number', label: 'Track Number' },
          { key: 'duration_seconds', type: 'number', label: 'Duration (seconds)' },
          { key: 'lyrics', type: 'text', label: 'Lyrics' }
        ]
      }
    })
  }
}


