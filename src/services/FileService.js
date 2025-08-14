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

  // Override create flow: when an upload has already created the record,
  // we receive { upload: <id>, title?, category_id? } and should update that row.
  async create(payload) {
    const uploadId = payload && payload.upload
    if (uploadId != null) {
      const updateData = {}
      if (Object.prototype.hasOwnProperty.call(payload, 'title')) updateData.title = payload.title
      if (Object.prototype.hasOwnProperty.call(payload, 'category_id')) updateData.category_id = payload.category_id
      // Remove the synthetic field to avoid confusion and avoid sending empty create payload
      try { delete payload.upload } catch (e) {}
      if (Object.keys(updateData).length > 0) {
        return super.put(`/${encodeURIComponent(uploadId)}`, updateData)
      }
      return super.get(`/${encodeURIComponent(uploadId)}`)
    }
    // Without an upload, backend validation would fail. Enforce usage.
    const err = { status: 400, message: 'File upload is required', data: { errors: ['upload is required'] } }
    if (this.onError) await this.onError(err)
    throw err
  }
}



