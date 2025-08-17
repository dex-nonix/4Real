<!-- ChatHeader.vue -->
<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import { ref } from 'vue';

const props = defineProps({
  persona: { type: Object, required: true },
  currentSession: { type: Object, required: true },
  currentHistory: { type: Object, required: true }
});

const emit = defineEmits(['viewHistory', 'closeChat', 'renameHistory']);

const isEditingTitle = ref(false);
const editedTitle = ref('');

const startEditing = () => {
  editedTitle.value = props.currentHistory.title;
  isEditingTitle.value = true;
};

const saveTitle = () => {
  emit('renameHistory', props.currentHistory.id, editedTitle.value);
  isEditingTitle.value = false;
};

const cancelEditing = () => {
  isEditingTitle.value = false;
};

// Avatar fallback logic
const getAvatarDisplay = () => {
  if (props.persona.avatar_url) {
    return { image: props.persona.avatar_url, fallback: null };
  }
  // Use first 2 characters of persona name
  const initials = props.persona.name.substring(0, 2).toUpperCase();
  return { image: null, fallback: initials };
};
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
        <span class="font-bold text-900">{{ persona.name }}</span>
        <div v-if="!isEditingTitle" class="text-sm text-500 cursor-pointer hover:text-700" @click="startEditing">
          {{ currentHistory.title }}
        </div>
        <div v-else class="flex align-items-center gap-2">
          <input 
            v-model="editedTitle" 
            @keyup.enter="saveTitle"
            @keyup.esc="cancelEditing"
            class="p-inputtext p-inputtext-sm"
            style="width: 200px;"
            ref="titleInput"
            @mounted="titleInput?.focus()"
          />
          <Button icon="pi pi-check" size="small" @click="saveTitle" />
          <Button icon="pi pi-times" size="small" severity="secondary" @click="cancelEditing" />
        </div>
      </div>
    </div>

    <div class="flex align-items-center gap-1">
      <!-- opens a popdown(not dialog) with the list of history, also to delete there and rename the history -->
      <Button icon="pi pi-history" text rounded severity="secondary" @click="emit('viewHistory')" v-tooltip.bottom="'View History'" />
      <!-- optional as its for use when in a sidepane so its optionally shown, but normally hidden -->
      <Button icon="pi pi-times" text rounded severity="secondary" @click="emit('closeChat')" v-tooltip.bottom="'Close Chat'"/>
    </div>
  </header>
</template>