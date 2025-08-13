// src/services/AIAnalysisResultService.js
import CrudService from '@/services/CrudService.js'

export default class AIAnalysisResultService extends CrudService {
  constructor() {
    super('ai-analysis-results', {
      table: {
        columns: [
          { field: 'track_id', header: 'Track ID', type: 'text', sortable: true },
          { field: 'provider_id', header: 'Provider ID', type: 'text', sortable: true },
          { field: 'analysis_type', header: 'Type', type: 'text', sortable: true },
          { field: 'model_name', header: 'Model', type: 'text', sortable: true }
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
          { key: 'track_id', type: 'text', label: 'Track ID', required: true },
          { key: 'provider_id', type: 'text', label: 'Provider ID', required: true },
          { key: 'analysis_type', type: 'text', label: 'Analysis Type', required: true },
          { key: 'model_name', type: 'text', label: 'Model Name' },
          { key: 'result_json', type: 'json', label: 'Result (JSON)' }
        ]
      }
    })
  }
}


