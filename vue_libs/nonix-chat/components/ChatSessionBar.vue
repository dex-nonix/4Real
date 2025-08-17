<!-- ChatSessionBar.vue -->
<script setup>
import Button from 'primevue/button';
import Divider from 'primevue/divider';
import Avatar from 'primevue/avatar';
import { ref } from 'vue';

const props = defineProps({
  personas: { type: Array, required: true, default: () => [] },
  currentPersonaId: { type: [String, Number, null], required: false, default: null },
  currentSessionId: { type: [String, Number, null], required: false, default: null }
});

const emit = defineEmits(['personaSelected', 'sessionSelected', 'addPersona']);

const expandedPersonas = ref(new Set());

const togglePersona = (personaId) => {
  if (expandedPersonas.value.has(personaId)) {
    expandedPersonas.value.delete(personaId);
  } else {
    expandedPersonas.value.add(personaId);
  }
};

const getAvatarDisplay = (persona) => {
  if (!persona) return { image: null, fallback: '??' };
  
  if (persona.avatar_url) {
    return { image: persona.avatar_url, fallback: null };
  }
  const initials = persona.name?.substring(0, 2).toUpperCase() || '??';
  return { image: null, fallback: initials };
};
</script>

<template>
  <aside class="h-full surface-section flex-shrink-0 surface-border select-none">
    <div class="flex flex-column h-full">
      <div class="flex flex-column flex-grow-1 overflow-y-auto">
        <div v-for="persona in personas" :key="persona.id" class="persona-section">
          <!-- Persona Header -->
          <div 
            class="persona-header cursor-pointer p-2 hover:surface-200"
            :class="{ 'surface-200': currentPersonaId === persona.id }"
            @click="togglePersona(persona.id)"
          >
            <div class="flex align-items-center gap-2">
              <Avatar 
                :image="getAvatarDisplay(persona).image" 
                :label="getAvatarDisplay(persona).fallback"
                size="large" 
                shape="circle"
              />
              <div class="flex flex-column flex-grow-1">
                <span class="font-bold text-sm">{{ persona.name }}</span>
                <span class="text-xs text-500">{{ persona.sessions?.length || 0 }} sessions</span>
              </div>
              <i class="pi" :class="expandedPersonas.has(persona.id) ? 'pi-chevron-down' : 'pi-chevron-right'"></i>
            </div>
          </div>

          <!-- Sessions for this persona -->
          <div v-if="expandedPersonas.has(persona.id)" class="sessions-list">
            <div 
              v-for="session in persona.sessions" 
              :key="session.id"
              class="session-item cursor-pointer p-2 pl-4 hover:surface-100"
              :class="{ 'surface-100 border-left-2 border-blue-500': currentSessionId === session.id }"
              @click="emit('sessionSelected', session.id)"
            >
              <div class="flex align-items-center gap-2">
                <span v-if="session.session_icon" class="text-lg">{{ session.session_icon }}</span>
                <span class="text-sm">{{ session.session_name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-auto flex-shrink-0">
        <Divider class="mb-1"/>
        <div class="p-2 mx-auto">
          <!-- opens menu with options to add a persona to chat with (new session) -->
          <Button
            icon="pi pi-plus"
            rounded
            severity="secondary"
            @click="emit('addPersona')"
            v-tooltip.bottom="'Add New Persona Chat'"
          />
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.persona-section {
  border-bottom: 1px solid var(--surface-border);
}

.persona-header:hover {
  background-color: var(--surface-100);
}

.sessions-list {
  background-color: var(--surface-50);
}

.session-item:hover {
  background-color: var(--surface-100);
}
</style>
