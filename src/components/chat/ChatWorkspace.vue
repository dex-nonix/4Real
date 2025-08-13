<template>
  <div class="chat-workspace">
    <ChatHeader
      :title="activeTitle"
      :persona-name="activePersonaName"
      @new-session="$emit('new-session')"
    />

    <div class="grid">
      <div v-if="enableLeftPanel" class="col-12 md:col-3">
        <LeftPanel
          :personas="personas"
          :selected-persona-id="selectedPersonaId"
          :sessions="sessions"
          @update:selected-persona-id="$emit('update:selected-persona-id', $event)"
          @open-session="$emit('open-session', $event)"
          @new-session="$emit('new-session')"
        />
      </div>

      <div class="col-12" :class="enableLeftPanel && enableRightPanel ? 'md:col-6' : (enableLeftPanel || enableRightPanel) ? 'md:col-9' : 'md:col-12'">
        <div class="p-2 surface-50 border-round" style="min-height: 240px;">
          <ChatTabs
            :tabs="openTabs"
            :active-tab-id="activeTabId"
            @activate-tab="$emit('activate-tab', $event)"
            @close-tab="$emit('close-tab', $event)"
          />
          <div class="mt-3">
            <template v-if="activeSessionId">
              <div v-if="activeMessages.length === 0" class="p-2 text-600">No messages yet</div>
              <ChatMessageList :messages="activeMessages" />
              <div class="mt-2">
                <ChatComposer :session-id="activeSessionId" v-model="draftValue" @send="(c)=>$emit('send', c)" @retry="$emit('retry')" />
              </div>
            </template>
            <template v-else>
              <div class="p-3 text-600">Select a session or create a new one to start chatting.</div>
            </template>
          </div>
        </div>
      </div>

      <div v-if="enableRightPanel" class="col-12 md:col-3">
        <RightPanel />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import ChatHeader from '@/components/chat/header/ChatHeader.vue'
import LeftPanel from '@/components/chat/panel/LeftPanel.vue'
import RightPanel from '@/components/chat/panel/RightPanel.vue'
import ChatTabs from '@/components/chat/tabs/ChatTabs.vue'
import ChatMessageList from '@/components/chat/messages/ChatMessageList.vue'
import ChatComposer from '@/components/chat/composer/ChatComposer.vue'

const props = defineProps({
  enableLeftPanel: { type: Boolean, default: true },
  enableRightPanel: { type: Boolean, default: true },
  personas: { type: Array, default: () => [] },
  selectedPersonaId: { type: [Number, String], default: null },
  sessions: { type: Array, default: () => [] },
  openTabs: { type: Array, default: () => [] },
  activeTabId: { type: [String, null], default: null },
  messagesBySession: { type: Object, default: () => ({}) },
  draftsBySession: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:selected-persona-id','open-session','new-session','activate-tab','close-tab','load-messages','update-draft','send','retry'])

const activeTitle = computed(() => {
  const active = props.openTabs.find(t => t.id === props.activeTabId)
  return active ? active.title : 'No session'
})

const activePersonaName = computed(() => {
  if (!props.selectedPersonaId) return ''
  const p = props.personas.find(p => p.id === props.selectedPersonaId || p.value === props.selectedPersonaId)
  return p ? (p.label || p.name) : ''
})

const activeSessionId = computed(() => {
  const active = props.openTabs.find(t => t.id === props.activeTabId)
  return active?.sessionId || null
})

const activeMessages = computed(() => {
  return (props.messagesBySession && activeSessionId.value != null)
    ? (props.messagesBySession[activeSessionId.value] || [])
    : []
})

const draftValue = computed({
  get() {
    if (!activeSessionId.value) return ''
    return props.draftsBySession?.[activeSessionId.value] || ''
  },
  set(v) {
    if (!activeSessionId.value) return
    emit('update-draft', { sessionId: activeSessionId.value, text: v || '' })
  }
})

watch(activeSessionId, (sid) => {
  if (!sid) return
  const loaded = !!(props.messagesBySession && props.messagesBySession[sid])
  if (!loaded) emit('load-messages', sid)
})
</script>

<style scoped>
.chat-workspace { width: 100%; }
</style>


