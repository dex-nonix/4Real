/**
 * Core download function - handles URL + filename directly
 * @param {string} url - The URL to download
 * @param {string} filename - The filename for download
 * @throws {Error} If no URL provided
 */
export const downloadUrl = (url, filename = 'download') => {
  if (!url) {
    throw new Error('No URL provided for download')
  }

  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * Download a file object - extracts URL and filename, calls downloadUrl
 * @param {Object} file - File object with .url and .original_filename properties
 * @throws {Error} If file has no URL
 */
export const downloadFile = (file) => {
  if (!file?.url) {
    throw new Error('File has no URL for download')
  }

  const filename = file.original_filename || 'download'
  downloadUrl(file.url, filename)
}
