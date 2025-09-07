// App config - environment-based API base URL
// Vite exposes import.meta.env.VITE_* variables

const origin = typeof window !== 'undefined' ? window.location.origin : 'https://dev.local:8443'
const parsed = new URL(origin)
const wsScheme = parsed.protocol === 'https:' ? 'wss' : 'ws'
export const API_BASE_URL = `${origin}/api`
export const WS_BASE_URL = `${wsScheme}://${parsed.host}`


