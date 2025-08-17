<!-- HistoryManagementPanel.vue -->
<template>
  <div class="history-panel">
    <div class="flex justify-content-between align-items-center mb-3">
      <h3 class="m-0">Conversation History</h3>
      <Button 
        icon="pi pi-plus" 
        size="small" 
        @click="createNewHistory"
        label="New Chat"
      />
    </div>

    <div class="histories-list">
      <div 
        v-for="history in histories" 
        :key="history.id"
        class="history-item cursor-pointer p-2 border-round hover:surface-100"
        :class="{ 'surface-100 border-left-2 border-blue-500': currentHistoryId === history.id }"
        @click="selectHistory(history.id)"
      >
        <div class="flex justify-content-between align-items-center">
          <span class="font-medium">{{ history.title }}</span>
          <span class="text-xs text-500">{{ history.message_count }} messages</span>
        </div>
        <div class="flex gap-2 mt-2">
          <Button 
            icon="pi pi-pencil" 
            size="small" 
            text 
            @click.stop="editHistory(history)"
            v-tooltip.bottom="'Rename History'"
          />
          <Button 
            icon="pi pi-trash" 
            size="small" 
            text 
            severity="danger"
            @click.stop="deleteHistory(history.id)"
            v-tooltip.bottom="'Delete History'"
          />
        </div>
      </div>
    </div>

    <!-- New History Dialog -->
    <Dialog 
      v-model:visible="showNewHistoryDialog" 
      modal 
      header="Create New Conversation"
      :style="{ width: '400px' }"
    >
      <div class="flex flex-column gap-3">
        <label for="historyTitle" class="font-medium">Conversation Title</label>
        <InputText 
          id="historyTitle"
          v-model="newHistoryTitle" 
          placeholder="e.g., Album Discussion, Music Chat"
          class="w-full"
        />
      </div>
      <template #footer>
        <Button label="Cancel" text @click="showNewHistoryDialog = false" />
        <Button label="Create" @click="confirmCreateHistory" />
      </template>
    </Dialog>

    <!-- Edit History Dialog -->
    <Dialog 
      v-model:visible="showEditHistoryDialog" 
      modal 
      header="Rename Conversation"
      :style="{ width: '400px' }"
    >
      <div class="flex flex-column gap-3">
        <label for="editHistoryTitle" class="font-medium">New Title</label>
        <InputText 
          id="editHistoryTitle"
          v-model="editHistoryTitle" 
          placeholder="Enter new title"
          class="w-full"
        />
      </div>
      <template #footer>
        <Button label="Cancel" text @click="showEditHistoryDialog = false" />
        <Button label="Save" @click="confirmEditHistory" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import { ref } from 'vue';

const props = defineProps({
  histories: { type: Array, required: true, default: () => [] },
  currentHistoryId: { type: [String, Number, null], required: false, default: null },
  sessionId: { type: [String, Number, null], required: false, default: null }
});

const emit = defineEmits(['historySelected', 'createHistory', 'updateHistory', 'deleteHistory']);

const showNewHistoryDialog = ref(false);
const showEditHistoryDialog = ref(false);
const newHistoryTitle = ref('');
const editHistoryTitle = ref('');
const editingHistory = ref(null);

const createNewHistory = () => {
  newHistoryTitle.value = '';
  showNewHistoryDialog.value = true;
};

const confirmCreateHistory = () => {
  if (newHistoryTitle.value.trim()) {
    emit('createHistory', props.sessionId, newHistoryTitle.value.trim());
    showNewHistoryDialog.value = false;
  }
};

const editHistory = (history) => {
  editingHistory.value = history;
  editHistoryTitle.value = history.title;
  showEditHistoryDialog.value = true;
};

const confirmEditHistory = () => {
  if (editHistoryTitle.value.trim() && editingHistory.value) {
    emit('updateHistory', props.sessionId, editingHistory.value.id, editHistoryTitle.value.trim());
    showEditHistoryDialog.value = false;
    editingHistory.value = null;
  }
};

const selectHistory = (historyId) => {
  emit('historySelected', historyId);
};

const deleteHistory = (historyId) => {
  if (confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
    emit('deleteHistory', props.sessionId, historyId);
  }
};
</script>

<style scoped>
.history-panel {
  padding: 1rem;
}

.histories-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  transition: all 0.2s ease;
}

.history-item:hover {
  transform: translateX(2px);
}
</style>
