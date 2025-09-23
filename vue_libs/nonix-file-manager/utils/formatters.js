/**
 * Format date string
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString()
}

/**
 * Format duration in seconds to HH:MM:SS or MM:SS
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
export const formatDuration = (seconds) => {
  if (!seconds) return 'Unknown'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

/**
 * Format file size in human readable format
 * Note: This is a wrapper - actual implementation uses injected fileTypeManager
 * @param {number} bytes - File size in bytes
 * @param {Object} fileTypeManager - Injected file type manager service
 * @returns {string} Formatted size string
 */
export const formatFileSize = (bytes, fileTypeManager) => {
  if (!bytes) return ''
  return fileTypeManager?.formatFileSize(bytes) || ''
}
