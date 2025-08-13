// src/services/AIAnalysisResultService.js
import CrudService from '@/services/CrudService.js'

export default class AIAnalysisResultService extends CrudService {
  constructor() {
    super('ai-analysis-results', {
      table: {
        columns: [
          { field: 'track_id', header: 'Track', type: 'fk_display', sortable: true, props: { entity: 'tracks' } },
          { field: 'provider_id', header: 'Provider', type: 'fk_display', sortable: true, props: { entity: 'ai-providers' } },
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
          { key: 'track_id', type: 'fk_select', label: 'Track', required: true, props: { entity: 'tracks', search: true } },
          { key: 'provider_id', type: 'fk_select', label: 'Provider', required: true, props: { entity: 'ai-providers', search: true } },
          { key: 'analysis_type', type: 'text', label: 'Analysis Type', required: true },
          { key: 'model_name', type: 'text', label: 'Model Name' },
          { key: 'result_json', type: 'json', label: 'Result (JSON)' }
        ]
      }
    })
  }
}


