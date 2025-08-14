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
          { key: 'upload', type: 'file_upload', label: 'Upload File', required: true },
          { key: 'storage_url', type: 'file_preview', label: 'Preview', displayOnly: true },
          { key: 'original_filename', type: 'text', label: 'Filename', displayOnly: true },
          { key: 'mime_type', type: 'text', label: 'MIME', displayOnly: true },
          { key: 'size_bytes', type: 'number', label: 'Size (bytes)', displayOnly: true }
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
    // New contract: File field provides a File object in formData.upload
    const file = payload && payload.upload
    if (file && typeof File !== 'undefined' && file instanceof File) {
      const res = await this.upload(file, { title: payload.title, category_id: payload.category_id })
      return res
    }
    // If an id was manually provided (rare), update metadata
    const uploadId = payload && typeof payload.upload === 'number' ? payload.upload : null
    if (uploadId != null) {
      const updateData = {}
      if (Object.prototype.hasOwnProperty.call(payload, 'title')) updateData.title = payload.title
      if (Object.prototype.hasOwnProperty.call(payload, 'category_id')) updateData.category_id = payload.category_id
      try { delete payload.upload } catch (e) {}
      return super.put(`/${encodeURIComponent(uploadId)}`, updateData)
    }
    const err = { status: 400, message: 'File upload is required', data: { errors: ['upload is required'] } }
    if (this.onError) await this.onError(err)
    throw err
  }

  // Prevent accidental duplicate upload by calling create() twice quickly
  async update(id, payload) {
    // Ignore any synthetic upload key on update
    if (payload && Object.prototype.hasOwnProperty.call(payload, 'upload')) {
      try { delete payload.upload } catch (e) {}
    }
    return super.update(id, payload)
  }
}



