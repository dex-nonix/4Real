import { NX_FILE_TYPES, detectFileType, getFileTypeByMime, getFileTypeByExtension } from '@nonix-file-manager/registries/file-types.js'

// File Type Manager - Service layer over NX_FILE_TYPES registry
export default class NxFileTypeManager {
    constructor(app) {
        // Start with built-in file types
        this.fileTypes = { ...NX_FILE_TYPES }
    }

    // Get file type configuration by key
    getFileType(key) {
        return this.fileTypes[key] || this.fileTypes.unknown
    }

    // Get all available file types
    getAllFileTypes() {
        return Object.entries(this.fileTypes).map(([key, config]) => ({
            key,
            ...config
        }))
    }

    // Get file types by category
    getFileTypesByCategory(category) {
        return Object.entries(this.fileTypes)
            .filter(([_, config]) => config.category === category)
            .map(([key, config]) => ({ key, ...config }))
    }

    // Detect file type from MIME type and filename
    detectFileType(mimeType, filename) {
        return detectFileType(mimeType, filename)
    }

    // Get file type by MIME type only
    getFileTypeByMime(mimeType) {
        return getFileTypeByMime(mimeType)
    }

    // Get file type by filename extension only
    getFileTypeByExtension(filename) {
        return getFileTypeByExtension(filename)
    }

    // Register a new file type at runtime
    registerFileType(key, config) {
        this.fileTypes[key] = {
            icon: 'pi-file',
            category: 'custom',
            color: '#6c757d',
            mimeTypes: [],
            extensions: [],
            displayName: key,
            ...config
        }
    }

    // Update existing file type
    updateFileType(key, updates) {
        if (this.fileTypes[key]) {
            this.fileTypes[key] = { ...this.fileTypes[key], ...updates }
        }
    }

    // Remove custom file type (can't remove built-ins)
    unregisterFileType(key) {
        if (this.fileTypes[key] && !NX_FILE_TYPES[key]) {
            delete this.fileTypes[key]
        }
    }

    // Get file type icon class
    getIconClass(fileType) {
        const config = typeof fileType === 'string' ? this.getFileType(fileType) : fileType
        return `pi ${config.icon}`
    }

    // Get file type display name
    getDisplayName(fileType) {
        const config = typeof fileType === 'string' ? this.getFileType(fileType) : fileType
        return config.displayName || config.key
    }

    // Get file type color
    getColor(fileType) {
        const config = typeof fileType === 'string' ? this.getFileType(fileType) : fileType
        return config.color
    }

    // Check if file type supports preview
    supportsPreview(fileType) {
        const config = typeof fileType === 'string' ? this.getFileType(fileType) : fileType
        return ['image', 'audio', 'video'].includes(config.category)
    }

    // Format file size
    formatFileSize(bytes) {
        if (!bytes || bytes === 0) return '0 B'

        const units = ['B', 'KB', 'MB', 'GB', 'TB']
        let size = bytes
        let unitIndex = 0

        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024
            unitIndex++
        }

        return `${size.toFixed(1)} ${units[unitIndex]}`
    }

    // Get file extension from filename
    getFileExtension(filename) {
        if (!filename) return ''
        const match = filename.toLowerCase().match(/\.([^.]+)$/)
        return match ? match[1] : ''
    }

    // Validate file against allowed types
    validateFileType(filename, mimeType, allowedTypes = []) {
        if (!allowedTypes || allowedTypes.length === 0) return true

        const fileType = this.detectFileType(mimeType, filename)
        return allowedTypes.includes(fileType.key) ||
               allowedTypes.includes(fileType.category) ||
               allowedTypes.some(type => fileType.mimeTypes.includes(type))
    }

    // Get suggested file types for a category
    getSuggestedTypes(category) {
        return this.getFileTypesByCategory(category)
    }

    // Get file type statistics
    getTypeStats() {
        const stats = {}
        Object.entries(this.fileTypes).forEach(([key, config]) => {
            const category = config.category
            if (!stats[category]) {
                stats[category] = { count: 0, types: [] }
            }
            stats[category].count++
            stats[category].types.push(key)
        })
        return stats
    }
}

// Export singleton instance

