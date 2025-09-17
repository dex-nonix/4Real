export default class NxFileOperationsService {
  constructor(app) {
    this.app = app
    this.fileService = app._context.provides.files
    this.categoryService = app._context.provides['file-categories']
  }

  async copyFiles(fileIds, targetCategoryId) {
    try {
      const results = []
      for (const fileId of fileIds) {
        const file = await this.fileService.get(fileId)
        if (file.data) {
          // Create new file with same data but different category
          const newFile = {
            ...file.data,
            category_id: targetCategoryId,
            title: `${file.data.title} (Copy)`
          }
          delete newFile.id
          delete newFile.created_at
          delete newFile.updated_at

          const result = await this.fileService.create(newFile)
          results.push(result)
        }
      }
      return { success: true, results }
    } catch (error) {
      console.error('Copy files error:', error)
      return { success: false, error: error.message }
    }
  }

  async moveFiles(fileIds, targetCategoryId) {
    try {
      const results = []
      for (const fileId of fileIds) {
        const result = await this.fileService.update(fileId, {
          category_id: targetCategoryId
        })
        results.push(result)
      }
      return { success: true, results }
    } catch (error) {
      console.error('Move files error:', error)
      return { success: false, error: error.message }
    }
  }

  async renameFile(fileId, newTitle) {
    try {
      const result = await this.fileService.update(fileId, {
        title: newTitle
      })
      return { success: true, result }
    } catch (error) {
      console.error('Rename file error:', error)
      return { success: false, error: error.message }
    }
  }

  async createCategory(name, parentId = null) {
    try {
      const result = await this.categoryService.create({
        name: name,
        slug: name.toLowerCase().replace(/\s+/g, '-'),
        description: ''
      })
      return { success: true, result }
    } catch (error) {
      console.error('Create category error:', error)
      return { success: false, error: error.message }
    }
  }

  async deleteCategory(categoryId) {
    try {
      // Check if category has files
      const files = await this.fileService.list({ category_id: categoryId })
      if (files.data && files.data.length > 0) {
        return { success: false, error: 'Cannot delete category with files' }
      }

      const result = await this.categoryService.delete(categoryId)
      return { success: true, result }
    } catch (error) {
      console.error('Delete category error:', error)
      return { success: false, error: error.message }
    }
  }

  async getCategoryFileCount(categoryId) {
    try {
      const result = await this.fileService.list({
        category_id: categoryId,
        paginated: false
      })
      return result.data.data.length
    } catch (error) {
      console.error('Get category file count error:', error)
      return 0
    }
  }
}
