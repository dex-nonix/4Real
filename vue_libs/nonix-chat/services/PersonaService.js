import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class PersonaService extends NxCrudService {
  constructor(app) {
    super(app,'personas', {
      table: {
        columns: [
          { field: 'name', header: 'Name', type: 'text', sortable: true },
          { field: 'artist_id', header: 'Artist', type: 'fk_display', sortable: true, props: { entity: 'artists' } },
          { field: 'ai_model_mapping_id', header: 'Model Mapping', type: 'fk_display', sortable: true, props: { entity: 'ai-model-mappings', labelKey: 'name' } },
          { field: 'is_active', header: 'Active', type: 'boolean', sortable: true }
        ]
      },
      form: {
        fields: [
          { key: 'name', type: 'text', label: 'Name', required: true },
          { key: 'artist_id', type: 'fk_select', label: 'Artist (optional)', props: { entity: 'artists', search: true } },
          { key: 'ai_model_mapping_id', type: 'fk_select', label: 'Model Mapping (chat)', required: true, props: { entity: 'ai-model-mappings', search: true } },
          { key: 'is_active', type: 'boolean', label: 'Active' },
          { key: 'system_prompt', type: 'textarea', label: 'System Prompt' },
          { key: 'metadata_json', type: 'json', label: 'Metadata (JSON)' }
        ]
      }
    })
  }
}


