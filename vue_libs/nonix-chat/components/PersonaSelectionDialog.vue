<!-- PersonaSelectionDialog.vue -->
<template>
  <Dialog 
    :visible="visible" 
    @update:visible="updateVisible"
    modal 
    header="Select Persona to Chat With"
    :style="{ width: '600px' }"
  >
    <div v-if="loading" class="flex justify-content-center p-4">
      <ProgressSpinner />
    </div>
    
    <div v-else-if="personas.length === 0" class="flex justify-content-center p-4">
      <span class="text-500">No personas available</span>
    </div>
    
    <div v-else class="personas-grid">
      <div 
        v-for="persona in personas" 
        :key="persona.id"
        class="persona-card cursor-pointer p-3 border-round surface-border border-1 hover:surface-100"
        @click="selectPersona(persona)"
      >
        <div class="flex align-items-center gap-3">
          <Avatar 
            :image="persona.avatar_url" 
            :label="persona.name.substring(0, 2).toUpperCase()"
            size="large" 
            shape="circle"
          />
          <div class="flex flex-column flex-grow-1">
            <h3 class="mt-0 mb-1 text-lg">{{ persona.name }}</h3>
            <p v-if="persona.system_prompt" class="text-sm text-500 mb-2">
              {{ persona.system_prompt.substring(0, 100) }}{{ persona.system_prompt.length > 100 ? '...' : '' }}
            </p>
            <div class="flex align-items-center gap-2">
              <span class="text-xs text-500">{{ persona.sessions?.length || 0 }} active sessions</span>
              <i v-if="persona.is_active" class="pi pi-check-circle text-green-500"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" text @click="close" />
    </template>
  </Dialog>
</template>

<script setup>
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
import ProgressSpinner from 'primevue/progressspinner';
import { ref, watch, inject } from 'vue';

const props = defineProps({
  visible: { type: Boolean, required: true }
});

const emit = defineEmits(['update:visible', 'personaSelected']);

// Service - injected singleton
const chatService = inject('chat-service');

// State
const personas = ref([]);
const loading = ref(false);

// Load personas when dialog opens
const loadPersonas = async () => {
  try {
    loading.value = true;
    const response = await chatService.getPersonas();
    // Handle ChatService response structure: {data: Array, total: number}
    personas.value = response.data || [];
  } catch (error) {
    console.error('Failed to load personas:', error);
    personas.value = [];
  } finally {
    loading.value = false;
  }
};

// Watch for dialog visibility and load data
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    loadPersonas();
  }
});

const updateVisible = (value) => {
  emit('update:visible', value);
};

const close = () => {
  emit('update:visible', false);
};

const selectPersona = (persona) => {
  emit('personaSelected', persona);
  close();
};
</script>

<style scoped>
.personas-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.persona-card {
  transition: all 0.2s ease;
}

.persona-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>
