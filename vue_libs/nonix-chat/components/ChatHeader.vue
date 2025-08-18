<!-- ChatHeader.vue -->
<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Menu from 'primevue/menu';
import { ref, h } from 'vue';

const props = defineProps({
  persona: { type: Object, required: false, default: null },
  currentSession: { type: Object, required: false, default: null },
  currentHistory: { type: Object, required: false, default: null }
});

const emit = defineEmits(['viewHistory', 'closeChat', 'renameHistory', 'clearMessages', 'deleteSession']);

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

// Avatar fallback logic with null safety
const getAvatarDisplay = () => {
  if (!props.persona) {
    return { image: null, fallback: '??' };
  }
  
  if (props.persona.avatar_url) {
    return { image: props.persona.avatar_url, fallback: null };
  }
  // Use first 2 characters of persona name
  const initials = props.persona.name?.substring(0, 2).toUpperCase() || '??';
  return { image: null, fallback: initials };
};

// Custom item component that transforms in the menu
const CustomMenuItem = {
  name: 'CustomMenuItem',
  props: ['item'],
  data() {
    return {
      showConfirm: false
    };
  },
  render() {
    if (!this.showConfirm) {
      return h('div', {
        class: 'flex align-items-center gap-2 p-2 cursor-pointer',
        onClick: (event) => {
          event.stopPropagation();
          this.showConfirm = true;
        }
      }, [
        h('i', { class: this.item.icon }),
        h('span', this.item.label)
      ]);
    } else {
      return h('div', {
        class: 'flex align-items-center gap-2 p-2'
      }, [
        h('span', {
          class: 'text-sm text-red-500 mr-2'
        }, `${this.item.label}?`),
        h('button', {
          class: 'p-button p-button-sm p-button-danger mr-1',
          onClick: (event) => {
            event.stopPropagation();
            this.confirm();
          }
        }, '✓'),
        h('button', {
          class: 'p-button p-button-sm p-button-secondary',
          onClick: (event) => {
            event.stopPropagation();
            this.cancel();
          }
        }, '✗')
      ]);
    }
  },
  methods: {
    confirm() {
      this.item.command();
      this.showConfirm = false;
      // Emit event to close menu
      this.$emit('close-menu');
    },
    cancel() {
      this.showConfirm = false;
    }
  }
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
    command: () => {
      if (props.currentSession?.id) {
        emit('deleteSession', props.currentSession.id);
      }
    }
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
        <span class="font-bold text-900">{{ persona?.name || 'No Persona Selected' }}</span>
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
      <!-- delete button with dropdown menu -->
      <div class="relative" ref="deleteButtonRef">
        <Button 
          icon="pi pi-trash" 
          text 
          rounded 
          severity="danger" 
          @click="(event) => { console.log('Button clicked'); toggleDeleteMenu(event); }" 
          v-tooltip.bottom="'Delete Options'"
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
            <component :is="CustomMenuItem" :item="item" @close-menu="deleteMenu.hide()" />
          </template>
        </Menu>
      </div>
      <!-- optional as its for use when in a sidepane so its optionally shown, but normally hidden -->
      <Button icon="pi pi-times" text rounded severity="secondary" @click="emit('closeChat')" v-tooltip.bottom="'Close Chat'"/>
    </div>
  </header>
</template>