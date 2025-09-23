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
