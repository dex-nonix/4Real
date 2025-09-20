import NxBaseApiService from '@nonix-api/services/NxBaseApiService.js'

export default class NxFileManagerService extends NxBaseApiService {
  constructor(app) {
    super(app)
    this.basePath = () => '/file-manager'
  }

  // File Operations
  async uploadFile(file, title, categoryId) {
    return this.post('/upload', { file, title, categoryId })
  }

  async listFiles() {
    return this.get('/files')
  }

  async deleteFile(fileId) {
    return this.delete(`/files/${fileId}`)
  }

  async bulkDeleteFiles(fileIds) {
    return this.post('/bulk/delete', { fileIds })
  }

  async bulkCopyFiles(fileIds, targetCategoryId) {
    return this.post('/bulk/copy', { fileIds, targetCategoryId })
  }

  async bulkMoveFiles(fileIds, targetCategoryId) {
    return this.post('/bulk/move', { fileIds, targetCategoryId })
  }


  async renameFile(fileId, newTitle) {
    return this.put(`/files/${fileId}/rename`, { newTitle })
  }

  async downloadFile(fileId) {
    // Return the download URL for the browser to handle
    const url = this.buildUrl(`/files/${fileId}/download`)
    window.open(url, '_blank')
    return { success: true }
  }

  async getFileUrl(fileId, action = 'preview') {
    // Return URL for file access (preview/stream/download)
    return this.buildUrl(`/files/${fileId}/${action}`)
  }

  async getPreviewUrl(fileId) {
    return this.getFileUrl(fileId, 'preview')
  }

  async getStreamUrl(fileId) {
    return this.getFileUrl(fileId, 'stream')
  }

  // Category Operations
  async getCategories() {
    return this.get('/categories')
  }

  async getCategoriesWithCounts() {
    return this.get('/categories/with-counts')
  }

  async createCategory(name) {
    return this.post('/categories', { name })
  }

  async updateCategory(categoryId, data) {
    return this.put(`/categories/${categoryId}`, data)
  }

  // Bulk Operations
  async bulkCopyFiles(fileIds, targetCategoryId) {
    return this.post('/bulk/copy', { fileIds, targetCategoryId })
  }

  async bulkMoveFiles(fileIds, targetCategoryId) {
    return this.post('/bulk/move', { fileIds, targetCategoryId })
  }
}
