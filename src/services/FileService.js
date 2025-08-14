// src/services/FileService.js
import CrudService from '@/services/CrudService.js'

export default class FileService extends CrudService {
  constructor() {
    super('files', {
      table: {
        columns: [
          { field: 'title', header: 'Title', type: 'text', sortable: true },
          { field: 'original_filename', header: 'Filename', type: 'text', sortable: true },
          { field: 'mime_type', header: 'MIME', type: 'text', sortable: true },
          { field: 'size_bytes', header: 'Size', type: 'number', sortable: true },
          { field: 'category_id', header: 'Category', type: 'fk_display', props: { entity: 'file-categories' } },
          { field: 'storage_url', header: 'Preview', type: 'file_preview' }
        ]
      },
      form: {
        fields: [
          { key: 'title', type: 'text', label: 'Title' },
          { key: 'category_id', type: 'fk_select', label: 'Category', props: { entity: 'file-categories', search: true } },
          { key: 'upload', type: 'file_upload', label: 'Upload File', required: true }
        ]
      }
    })
  }

  upload(file, { title, category_id } = {}) {
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)
    if (category_id != null) formData.append('category_id', String(category_id))
    return this.post('/upload', formData)
  }
}



