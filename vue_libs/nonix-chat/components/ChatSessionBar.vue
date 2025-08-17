<!-- ChatSessionBar.vue -->
<script setup>
import Button from 'primevue/button';
import Divider from 'primevue/divider';
import Avatar from 'primevue/avatar';

const props = defineProps({
  sessions: { type: Array, required: true, default: () => [] },
  currentSessionId: { type: [String, Number, null], required: false, default: null }
});

const emit = defineEmits(['sessionSelected', 'addSession']);

const getAvatarDisplay = (session) => {
  if (!session) return { image: null, fallback: '??' };
  
  if (session.avatar_url) {
    return { image: session.avatar_url, fallback: null };
  }
  
  // Use session name for initials since we have flat sessions
  const name = session.session_name || '??';
  const initials = name.substring(0, 2).toUpperCase();
  return { image: null, fallback: initials };
};
</script>

<template>
  <aside class="h-full surface-section flex-shrink-0 surface-border select-none">
    <div class="flex flex-column h-full">
      <div class="flex flex-column flex-grow-1 overflow-y-auto">
        <div v-if="sessions.length === 0" class="no-sessions p-3 text-center">
          <span class="text-500 text-sm">No sessions available</span>
        </div>
        <div 
          v-for="session in sessions" 
          :key="session.id" 
          class="session-item cursor-pointer p-3 hover:surface-200"
          :class="{ 'selected-session': currentSessionId === session.id }"
          @click="emit('sessionSelected', session.id)"
        >
          <Avatar 
            :image="getAvatarDisplay(session).image" 
            :label="getAvatarDisplay(session).fallback"
            size="large" 
            shape="circle"
          />
        </div>
      </div>

      <div class="mt-auto flex-shrink-0">
        <Divider class="mb-1"/>
        <div class="p-2 mx-auto">
          <Button
            icon="pi pi-plus"
            rounded
            severity="secondary"
            @click="emit('addSession')"
            v-tooltip.bottom="'Add New Session'"
          />
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.session-item {
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: 1px solid var(--surface-border);
  transition: all 0.2s ease;
}

.session-item:hover {
  background-color: var(--surface-200);
}

.selected-session {
  background-color: var(--primary-color);
  color: var(--primary-color-text);
}

.selected-session:hover {
  background-color: var(--primary-600);
}
</style>
