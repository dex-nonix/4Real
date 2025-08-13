// src/hooks/useChatInstance.js
import { reactive, toRefs } from 'vue'
import ChatRuntimeService from '@/services/ChatRuntimeService.js'

function loadFromStorage(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch { return fallback }
}

function saveToStorage(key, value) {
  try { window.localStorage.setItem(key, JSON.stringify(value)) } catch {}
}

export default function useChatInstance(options) {
  const { instanceId, persistKey = `chat:${instanceId}` } = options || {}
  if (!instanceId) throw new Error('useChatInstance requires instanceId')

  const api = new ChatRuntimeService()

  const state = reactive({
    personas: [],
    sessions: [],
    openTabs: loadFromStorage(`${persistKey}:tabs`, []),
    activeTabId: loadFromStorage(`${persistKey}:active`, null),
    messagesBySession: {},
    draftsBySession: loadFromStorage(`${persistKey}:drafts`, {}),
    availableToolsByPersona: {},
    mcpServers: [],
    loading: false,
    error: null,
  })

  function persist() {
    saveToStorage(`${persistKey}:tabs`, state.openTabs)
    saveToStorage(`${persistKey}:active`, state.activeTabId)
    saveToStorage(`${persistKey}:drafts`, state.draftsBySession)
  }

  async function loadPersonas() {
    try {
      state.loading = true
      const res = await fetch(`${api.baseURL}/personas/selector`)
      const body = await res.json().catch(() => null)
      state.personas = body?.data || []
    } catch (e) {
      state.error = e
    } finally { state.loading = false }
  }

  async function loadSessions(params = {}) {
    const { data } = await api.listSessions(params)
    state.sessions = data?.data || data || []
  }

  function findTabBySession(sessionId) {
    return state.openTabs.find(t => t.sessionId === sessionId) || null
  }

  function activateTab(tabId) {
    state.activeTabId = tabId
    persist()
  }

  async function openSession(sessionId) {
    const existing = findTabBySession(sessionId)
    if (existing) { activateTab(existing.id); return existing }
    const { data } = await api.getSession(sessionId)
    const sess = data?.data || data
    const tab = { id: `${instanceId}:${sessionId}`, sessionId, title: sess?.title || `Session ${sessionId}` }
    state.openTabs.push(tab)
    activateTab(tab.id)
    await loadMessages(sessionId)
    return tab
  }

  async function createSession({ personaId, title }) {
    const payload = { persona_id: personaId, title }
    const { data } = await api.createSession(payload)
    const sess = data?.data || data
    state.sessions.unshift(sess)
    return openSession(sess.id)
  }

  function closeTab(tabId) {
    const idx = state.openTabs.findIndex(t => t.id === tabId)
    if (idx >= 0) state.openTabs.splice(idx, 1)
    if (state.activeTabId === tabId) {
      state.activeTabId = state.openTabs.length ? state.openTabs[0].id : null
    }
    persist()
  }

  async function loadMessages(sessionId) {
    const { data } = await api.listMessages(sessionId)
    state.messagesBySession[sessionId] = data?.data || data || []
  }

  async function sendMessage(sessionId, content) {
    // optimistic user message append
    const user = { id: Date.now(), session_id: sessionId, role: 'user', content_json: content, created_at: new Date().toISOString() }
    state.messagesBySession[sessionId] = (state.messagesBySession[sessionId] || []).concat(user)
    const { data } = await api.send(sessionId, content)
    const asst = data?.data || data
    state.messagesBySession[sessionId] = (state.messagesBySession[sessionId] || []).concat(asst)
  }

  async function retryLast(sessionId) {
    const { data } = await api.retry(sessionId)
    const asst = data?.data || data
    state.messagesBySession[sessionId] = (state.messagesBySession[sessionId] || []).concat(asst)
  }

  async function loadPersonaTools(personaId) {
    const { data } = await api.personaTools(personaId)
    state.availableToolsByPersona[personaId] = data?.data || data || []
  }

  async function loadMcpStatus() {
    const { data } = await api.mcpStatus()
    state.mcpServers = data?.data || data || []
  }

  return {
    ...toRefs(state),
    loadPersonas,
    loadSessions,
    openSession,
    createSession,
    closeTab,
    loadMessages,
    sendMessage,
    retryLast,
    loadPersonaTools,
    loadMcpStatus,
    activateTab,
  }
}


