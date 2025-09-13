# NxWebStt Frontend Implementation

## Overview
Frontend CRUD interface for STT configurations - separate from chat module.

## Frontend Module Structure
```
vue_libs/nonix-stt/
├── services/
│   └── NxSttConfigurationService.js  # Vue service for STT configs
```

## Required Implementation

### 1. Vue Service (vue_libs/nonix-stt/services/NxSttConfigurationService.js)
```javascript
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
```

### 2. Service Registration (src/appConfig.js)
**Add import:**
```javascript
import NxSttConfigurationService from '@nonix-stt/services/NxSttConfigurationService.js'
```

**Add to service object:**
```javascript
service: {
  // ... existing services
  "stt-configurations": (app) => new NxSttConfigurationService(app),
}
```

### 3. Route Registration (src/appConfig.js)
**Add to routes array:**
```javascript
routes: [
  // ... existing routes
  {type: "crud", entity: 'stt-configurations'},
]
```

### 4. Navigation Entry (vue_libs/nonix-advanced-layout/navItems.js)
**Add to AI section:**
```javascript
{
  label: 'AI',
  icon: 'pi pi-brain',
  items: [
    // ... existing AI items
    {label: 'STT Configurations', icon: 'pi pi-microphone', to: '/stt-configurations'},
  ]
}
```

## API Endpoints Expected
- `GET /api/stt/` - List STT configurations
- `POST /api/stt/` - Create STT configuration
- `GET /api/stt/{id}` - Get STT configuration
- `PUT /api/stt/{id}` - Update STT configuration
- `DELETE /api/stt/{id}` - Delete STT configuration

## Features
- **CRUD Operations:** Full create, read, update, delete
- **Table View:** Sortable columns, pagination, filters
- **Form View:** Validation, dropdowns for model/device selection
- **Bulk Actions:** Delete multiple, export data
- **Search:** Filter configurations by name
- **Responsive:** Works on all screen sizes

## Implementation Notes
- **Separate Module:** STT is NOT part of chat - has its own module
- **Entity Name:** Uses 'stt-configurations' for URL routing
- **Display Name:** "STT Configurations" in navigation
- **Icon:** 'pi pi-microphone' for STT functionality
- **Location:** Under "AI" section in navigation menu
