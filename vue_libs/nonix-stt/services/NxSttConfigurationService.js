import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class NxSttConfigurationService extends NxCrudService {
  constructor(app) {
    super(app, 'stt-configurations', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'whisper_model', header: 'Model', type: 'text', sortable: true },
          { field: 'device', header: 'Device', type: 'text', sortable: true },
          { field: 'sample_rate', header: 'Sample Rate', type: 'number', sortable: true },
          { field: 'vad_enabled', header: 'VAD', type: 'boolean', sortable: true },
          { field: 'language', header: 'Language', type: 'text', sortable: true },
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
          { key: 'whisper_model', type: 'select', label: 'Whisper Model', required: true, 
            options: [
              { label: 'tiny', value: 'tiny' },
              { label: 'base', value: 'base' },
              { label: 'small', value: 'small' },
              { label: 'medium', value: 'medium' },
              { label: 'large', value: 'large' },
              { label: 'large-v2', value: 'large-v2' },
              { label: 'large-v3', value: 'large-v3' }
            ]
          },
          { key: 'device', type: 'select', label: 'Device', required: true,
            options: [
              { label: 'CPU', value: 'cpu' },
              { label: 'CUDA', value: 'cuda' },
              { label: 'MPS (Apple)', value: 'mps' }
            ]
          },
          { key: 'sample_rate', type: 'number', label: 'Sample Rate', required: true, min: 8000, max: 48000 },
          { key: 'vad_enabled', type: 'boolean', label: 'Voice Activity Detection' },
          { key: 'language', type: 'text', label: 'Language (optional)', placeholder: 'en, es, fr, de, etc.' },
          { key: 'is_active', type: 'boolean', label: 'Active' }
        ]
      }
    })
  }
}
