import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class NxFileService extends NxCrudService {
    constructor(app) {
        super(app, 'files', {
            table: {
                columns: [
                    {field: 'title', header: 'Title', type: 'text', sortable: true},
                    {field: 'original_filename', header: 'Filename', type: 'text', sortable: true},
                    {field: 'category_id', header: 'Category', type: 'fk_display', props: {entity: 'file-categories'}},
                    {field: 'storage_url', header: 'Preview', type: 'file_preview', props: { showSize: true, showCategory: true }}
                ]
            },
            form: {
                fields: [
                    {key: 'title', type: 'text', label: 'Title'},
                    {
                        key: 'category_id',
                        type: 'fk_select',
                        label: 'Category',
                        props: {entity: 'file-categories', search: true}
                    },
                    {key: 'upload', type: 'file_upload', label: 'Upload File', required: true},
                    {key: 'storage_url', type: 'file_preview', label: 'Preview', displayOnly: true, props: { showSize: true, showCategory: true }},
                    {key: 'original_filename', type: 'text', label: 'Filename', displayOnly: true}
                ]
            }
        })
    }

    upload(file, {title, category_id} = {}) {
        const formData = new FormData()
        formData.append('file', file)
        if (title) formData.append('title', title)
        if (category_id != null) formData.append('category_id', String(category_id))
        return this.post('/upload', formData)
    }

    uploadWithProgress(file, {title, category_id} = {}, onProgress) {
        const url = this.buildUrl(this.scopePath('/upload'))
        return new Promise((resolve, reject) => {
            try {
                const xhr = new XMLHttpRequest()
                xhr.open('POST', url, true)
                if (this.authToken) xhr.setRequestHeader('Authorization', `Bearer ${this.authToken}`)
                xhr.upload.onprogress = e => {
                    if (onProgress && e && e.lengthComputable) {
                        try {
                            onProgress(Math.round((e.loaded / e.total) * 100))
                        } catch {
                        }
                    }
                }
                xhr.onreadystatechange = () => {
                    if (xhr.readyState === 4) {
                        if (xhr.status >= 200 && xhr.status < 300) {
                            try {
                                resolve({status: xhr.status, ok: true, data: JSON.parse(xhr.responseText || '{}')})
                            } catch (err) {
                                resolve({status: xhr.status, ok: true, data: null})
                            }
                        } else {
                            let data = null
                            try {
                                data = JSON.parse(xhr.responseText || '{}')
                            } catch {
                            }
                            const error = {
                                status: xhr.status,
                                message: (data && (data.message || data.error)) || 'Upload failed',
                                data
                            }
                            reject(error)
                        }
                    }
                }
                const form = new FormData()
                form.append('file', file)
                if (title) form.append('title', title)
                if (category_id != null) form.append('category_id', String(category_id))
                xhr.send(form)
            } catch (err) {
                reject(err)
            }
        })
    }

    // Override create flow: when an upload has already created the record,
    // we receive { upload: <id>, title?, category_id? } and should update that row.
    async create(payload, options = {}) {
        // Supports: File object in payload.upload OR wrapper { file }
        const uploadVal = payload && payload.upload
        const onProgress = options && options.onProgress
        if (uploadVal) {
            let file = null
            if (typeof File !== 'undefined' && uploadVal instanceof File) {
                file = uploadVal
            } else if (typeof uploadVal === 'object') {
                file = uploadVal.file || null
            }
            if (file) {
                if (typeof onProgress === 'function' && typeof this.uploadWithProgress === 'function') {
                    return this.uploadWithProgress(file, {
                        title: payload.title,
                        category_id: payload.category_id
                    }, onProgress)
                }
                return this.upload(file, {title: payload.title, category_id: payload.category_id})
            }
        }
        // If an id was manually provided (rare), update metadata
        const uploadId = payload && typeof payload.upload === 'number' ? payload.upload : null
        if (uploadId != null) {
            const updateData = {}
            if (Object.prototype.hasOwnProperty.call(payload, 'title')) updateData.title = payload.title
            if (Object.prototype.hasOwnProperty.call(payload, 'category_id')) updateData.category_id = payload.category_id
            try {
                delete payload.upload
            } catch (e) {
            }
            return super.put(`/${encodeURIComponent(uploadId)}`, updateData)
        }
        const err = {status: 400, message: 'File upload is required', data: {errors: ['upload is required']}}
        if (this.onError) await this.onError(err)
        throw err
    }

    // Prevent accidental duplicate upload by calling create() twice quickly
    async update(id, payload) {
        // Ignore any synthetic upload key on update
        if (payload && Object.prototype.hasOwnProperty.call(payload, 'upload')) {
            try {
                delete payload.upload
            } catch (e) {
            }
        }
        return super.update(id, payload)
    }
}



