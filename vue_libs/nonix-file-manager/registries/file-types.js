// File type registry - central source of truth for all file types
export const NX_FILE_TYPES = {
    // Documents
    'pdf': {
        icon: 'pi-file-pdf',
        category: 'document',
        color: '#dc3545',
        mimeTypes: ['application/pdf'],
        extensions: ['.pdf'],
        displayName: 'PDF Document'
    },
    'doc': {
        icon: 'pi-file-word',
        category: 'document',
        color: '#2b579a',
        mimeTypes: ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        extensions: ['.doc', '.docx'],
        displayName: 'Word Document'
    },
    'xls': {
        icon: 'pi-file-excel',
        category: 'spreadsheet',
        color: '#217346',
        mimeTypes: ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
        extensions: ['.xls', '.xlsx'],
        displayName: 'Excel Spreadsheet'
    },
    'ppt': {
        icon: 'pi-file-powerpoint',
        category: 'presentation',
        color: '#d24726',
        mimeTypes: ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'],
        extensions: ['.ppt', '.pptx'],
        displayName: 'PowerPoint Presentation'
    },
    'txt': {
        icon: 'pi-file-text',
        category: 'text',
        color: '#6c757d',
        mimeTypes: ['text/plain', 'text/markdown'],
        extensions: ['.txt', '.md', '.rtf'],
        displayName: 'Text File'
    },

    // Images
    'image': {
        icon: 'pi-image',
        category: 'image',
        color: '#28a745',
        mimeTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml', 'image/*'],
        extensions: ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff'],
        displayName: 'Image'
    },

    // Audio/Video
    'audio': {
        icon: 'pi-volume-up',
        category: 'audio',
        color: '#6f42c1',
        mimeTypes: ['audio/*', 'audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg'],
        extensions: ['.mp3', '.wav', 'aac', '.ogg', '.flac', '.m4a'],
        displayName: 'Audio File'
    },
    'video': {
        icon: 'pi-video',
        category: 'video',
        color: '#fd7e14',
        mimeTypes: ['video/*', 'video/mp4', 'video/avi', 'video/mov', 'video/wmv'],
        extensions: ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.webm'],
        displayName: 'Video File'
    },

    // Code files
    'javascript': {
        icon: 'pi-code',
        category: 'code',
        color: '#f7df1e',
        mimeTypes: ['application/javascript', 'text/javascript'],
        extensions: ['.js', '.jsx', '.mjs'],
        displayName: 'JavaScript'
    },
    'python': {
        icon: 'pi-code',
        category: 'code',
        color: '#3776ab',
        mimeTypes: ['text/x-python'],
        extensions: ['.py', '.pyc', '.pyo', '.pyw'],
        displayName: 'Python'
    },
    'html': {
        icon: 'pi-code',
        category: 'web',
        color: '#e34c26',
        mimeTypes: ['text/html'],
        extensions: ['.html', '.htm'],
        displayName: 'HTML'
    },
    'css': {
        icon: 'pi-code',
        category: 'web',
        color: '#264de4',
        mimeTypes: ['text/css'],
        extensions: ['.css', '.scss', '.sass', '.less'],
        displayName: 'CSS'
    },
    'json': {
        icon: 'pi-code',
        category: 'data',
        color: '#000000',
        mimeTypes: ['application/json'],
        extensions: ['.json', '.geojson'],
        displayName: 'JSON'
    },

    // Archives
    'archive': {
        icon: 'pi-file-archive',
        category: 'archive',
        color: '#fd7e14',
        mimeTypes: ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed', 'application/x-tar'],
        extensions: ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        displayName: 'Archive'
    },

    // Executables
    'executable': {
        icon: 'pi-cog',
        category: 'executable',
        color: '#6c757d',
        mimeTypes: ['application/x-executable', 'application/octet-stream'],
        extensions: ['.exe', '.msi', '.dmg', '.app'],
        displayName: 'Executable'
    },

    // Default fallback
    'unknown': {
        icon: 'pi-file',
        category: 'unknown',
        color: '#6c757d',
        mimeTypes: [],
        extensions: [],
        displayName: 'File'
    }
}

// Helper functions for working with file types
export const getFileTypeByMime = (mimeType) => {
    if (!mimeType) return NX_FILE_TYPES.unknown

    // Exact match first
    for (const [key, config] of Object.entries(NX_FILE_TYPES)) {
        if (config.mimeTypes.includes(mimeType)) {
            return { ...config, key }
        }
    }

    // Wildcard match
    for (const [key, config] of Object.entries(NX_FILE_TYPES)) {
        if (config.mimeTypes.some(mt => mt.endsWith('/*') && mimeType.startsWith(mt.slice(0, -1)))) {
            return { ...config, key }
        }
    }

    return { ...NX_FILE_TYPES.unknown, key: 'unknown' }
}

export const getFileTypeByExtension = (filename) => {
    if (!filename) return { ...NX_FILE_TYPES.unknown, key: 'unknown' }

    const ext = filename.toLowerCase().match(/\.([^.]+)$/)?.[1]
    if (!ext) return { ...NX_FILE_TYPES.unknown, key: 'unknown' }

    for (const [key, config] of Object.entries(NX_FILE_TYPES)) {
        if (config.extensions.some(e => e === `.${ext}`)) {
            return { ...config, key }
        }
    }

    return { ...NX_FILE_TYPES.unknown, key: 'unknown' }
}

export const detectFileType = (mimeType, filename) => {
    // Try MIME type first
    let fileType = getFileTypeByMime(mimeType)
    if (fileType.key !== 'unknown') return fileType

    // Fall back to extension
    fileType = getFileTypeByExtension(filename)
    return fileType
}
