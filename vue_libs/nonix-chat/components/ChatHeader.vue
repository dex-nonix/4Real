<!-- ChatHeader.vue -->
<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Menu from 'primevue/menu';
import ConfirmMenuItem from './ConfirmMenuItem.vue';
import { ref, inject, watch } from 'vue';

const props = defineProps({
  persona: { type: Object, required: false, default: null },
  currentSession: { type: Object, required: false, default: null },
  currentHistory: { type: Object, required: false, default: null },
  menuItems: { type: Array, required: false, default: () => [] }
});

const emit = defineEmits(['viewHistory', 'renameHistory', 'clearMessages', 'deleteSession', 'menuItemClick']);

// Service injection
const chatService = inject('chat-service');

// Local persona state
const localPersona = ref(null);

// Watch for session changes and load persona data
watch(() => props.currentSession, async (newSession) => {
  if (newSession?.persona_id) {
    try {
      console.log('Loading persona for session:', newSession.persona_id);
      const response = await chatService.getPersona(newSession.persona_id);
      const personaData = response?.data || response;
      if (personaData) {
        localPersona.value = personaData;
        console.log('Persona loaded:', personaData.name);
      }
    } catch (error) {
      console.error('Failed to load persona:', error);
      localPersona.value = null;
    }
  } else {
    localPersona.value = null;
  }
}, { immediate: true });

const isEditingTitle = ref(false);
const editedTitle = ref('');
const deleteMenu = ref();

const startEditing = () => {
  if (!props.currentHistory) return;
  editedTitle.value = props.currentHistory.title;
  isEditingTitle.value = true;
};

const saveTitle = () => {
  if (!props.currentHistory) return;
  emit('renameHistory', props.currentHistory.id, editedTitle.value);
  isEditingTitle.value = false;
};

const cancelEditing = () => {
  isEditingTitle.value = false;
};

const toggleDeleteMenu = (event) => {
  console.log('Toggle menu clicked', event);
  if (deleteMenu.value) {
    deleteMenu.value.toggle(event);
  } else {
    console.error('deleteMenu ref is null');
  }
};

// Handle session deletion directly in ChatHeader
const handleDeleteSession = async () => {
  if (!props.currentSession?.id) {
    console.error('No session to delete');
    return;
  }

  try {
    console.log('Deleting session:', props.currentSession.id);
    const response = await chatService.deleteSession(props.currentSession.id);
    console.log('Session deletion response:', response);
    
    if (response && response.message) {
      // Simple success event - let parent handle UI updates
      emit('deleteSession', { 
        success: true, 
        sessionId: props.currentSession.id 
      });
    } else {
      // Simple error event
      emit('deleteSession', { 
        success: false, 
        sessionId: props.currentSession.id, 
        error: 'Failed to delete session' 
      });
    }
  } catch (error) {
    console.error('Failed to delete session:', error);
    // Simple error event
    emit('deleteSession', { 
      success: false, 
      sessionId: props.currentSession.id, 
      error 
    });
  }
};

// Avatar fallback logic with null safety
const getAvatarDisplay = () => {
  if (!localPersona.value) {
    return { image: null, fallback: '??' };
  }
  
  if (localPersona.value.avatar_url) {
    return { image: localPersona.value.avatar_url, fallback: null };
  }
  // Use first 2 characters of persona name
  const initials = localPersona.value.name?.substring(0, 2).toUpperCase() || '??';
  return { image: null, fallback: initials };
};

// Handle external menu item clicks
const handleMenuItemClick = (item) => {
  if (item.command) {
    item.command();
  }
  emit('menuItemClick', item);
};

// Menu items for delete dropdown - FIXED, NEVER CHANGE
const deleteMenuItems = [
  {
    label: 'Clear Messages',
    icon: 'pi pi-trash',
    command: () => emit('clearMessages')
  },
  {
    label: 'Delete Session',
    icon: 'pi pi-times',
    command: handleDeleteSession
  }
];
</script>

<template>
  <header class="flex justify-content-between align-items-center surface-section border-bottom-1 surface-border flex-shrink-0" style="height: 60px;">
    <div class="flex align-items-center gap-3">
      <Avatar 
        class="m-2" 
        :image="getAvatarDisplay().image" 
        :label="getAvatarDisplay().fallback"
        size="large" 
        shape="circle" 
      />
      <div class="flex flex-column">
        <span class="font-bold text-900">{{ localPersona?.name || 'No Persona Selected' }}</span>
        <div v-if="!isEditingTitle && currentHistory" class="text-sm text-500 cursor-pointer hover:text-700" @click="startEditing">
          {{ currentHistory.title }}
        </div>
        <div v-else-if="!currentHistory" class="text-sm text-500">
          No history selected
        </div>
        <div v-else class="flex align-items-center gap-2">
          <input 
            v-model="editedTitle" 
            @keyup.enter="saveTitle"
            @keyup.esc="cancelEditing"
            class="p-inputtext p-inputtext-sm"
            style="width: 100%; max-width: 200px;"
            ref="titleInput"
            @mounted="titleInput?.focus()"
          />
          <Button icon="pi pi-check" size="small" @click="saveTitle" />
          <Button icon="pi pi-times" size="small" severity="secondary" @click="cancelEditing" />
        </div>
      </div>
    </div>

    <div class="flex align-items-center gap-1">
      <!-- Built-in buttons first (left side) -->
      <Button icon="pi pi-history" text rounded severity="secondary" @click="emit('viewHistory')" aria-label="View History" />
      <div class="relative" ref="deleteButtonRef">
        <Button
          icon="pi pi-trash"
          text
          rounded
          severity="danger"
          @click="(event) => { console.log('Button clicked'); toggleDeleteMenu(event); }"
          aria-label="Delete Options"
          aria-haspopup="true"
          aria-controls="delete_menu"
        />
        <Menu
          ref="deleteMenu"
          id="delete_menu"
          :model="deleteMenuItems"
          :popup="true"
        >
          <template #item="{ item }">
            <component :is="ConfirmMenuItem" :item="item" @close-menu="deleteMenu.hide()" />
          </template>
        </Menu>
      </div>

      <!-- External menu items (right side) -->
      <Button
        v-for="item in menuItems"
        :key="item.label"
        :icon="item.icon"
        text
        rounded
        severity="secondary"
        @click="handleMenuItemClick(item)"
        :aria-label="item.label"
      />
    </div>
  </header>
</template>