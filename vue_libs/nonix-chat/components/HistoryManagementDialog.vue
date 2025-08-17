<!-- HistoryManagementPanel.vue -->
<template>
  <Dialog 
    :visible="visible" 
    @update:visible="updateVisible"
    modal 
    header="Chat History"
    :style="{ width: '600px' }"
  >
    <div v-if="loading" class="flex justify-content-center p-4">
      <ProgressSpinner />
    </div>
    
    <div v-else class="history-panel">
      <div class="flex justify-content-between align-items-center mb-3">
        <h3 class="m-0">Conversation History</h3>
        <Button 
          icon="pi pi-plus" 
          size="small" 
          @click="createNewHistory"
          label="New Chat"
        />
      </div>

      <div v-if="histories.length === 0" class="flex justify-content-center p-4">
        <span class="text-500">No conversation history available</span>
      </div>

      <div v-else class="histories-list">
        <div 
          v-for="historyItem in histories" 
          :key="historyItem.id"
          class="history-item cursor-pointer p-2 border-round hover:surface-100"
          :class="{ 'surface-100 border-left-2 border-blue-500': currentHistoryId === historyItem.id }"
          @click="selectHistory(historyItem.id)"
        >
          <div class="flex justify-content-between align-items-center">
            <span class="font-medium">{{ historyItem.title }}</span>
            <span class="text-xs text-500">{{ historyItem.message_count }} messages</span>
          </div>
          <div class="flex gap-2 mt-2">
            <Button 
              icon="pi pi-pencil" 
              size="small" 
              text 
              @click.stop="editHistory(historyItem)"
              v-tooltip.bottom="'Rename History'"
            />
            <Button 
              icon="pi pi-trash" 
              size="small" 
              text 
              severity="danger"
              @click.stop="deleteHistory(historyItem.id)"
              v-tooltip.bottom="'Delete History'"
            />
          </div>
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
  </Dialog>
</template>

<script setup>
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import { ref, watch, inject } from 'vue';

const props = defineProps({
  visible: { type: Boolean, required: true },
  sessionId: { type: [String, Number], required: true }
});

const emit = defineEmits(['update:visible', 'historySelected', 'createHistory', 'updateHistory', 'deleteHistory']);

// Service - injected singleton
const chatService = inject('chat-service');

// State
const histories = ref([]);
const loading = ref(false);
const currentHistoryId = ref(null);

// Dialog states
const showNewHistoryDialog = ref(false);
const showEditHistoryDialog = ref(false);
const newHistoryTitle = ref('');
const editHistoryTitle = ref('');
const editingHistory = ref(null);

// Load histories when dialog opens
const loadHistories = async () => {
  if (!props.sessionId) return;
  
  try {
    loading.value = true;
    const response = await chatService.getHistories(props.sessionId);
    
    // ChatService now returns clean data directly
    histories.value = response || [];
  } catch (error) {
    console.error('Failed to load histories:', error);
    histories.value = [];
  } finally {
    loading.value = false;
  }
};

// Watch for dialog visibility and load data
watch(() => props.visible, (newVisible) => {
  if (newVisible && props.sessionId) {
    loadHistories();
  }
});

const updateVisible = (value) => {
  emit('update:visible', value);
};

const close = () => {
  emit('update:visible', false);
};

const selectHistory = (historyId) => {
  currentHistoryId.value = historyId;
  emit('historySelected', historyId);
  close();
};

const createNewHistory = () => {
  showNewHistoryDialog.value = true;
};

const confirmCreateHistory = async () => {
  if (!newHistoryTitle.value.trim()) return;
  
  try {
    await chatService.createHistory(props.sessionId, newHistoryTitle.value.trim());
    newHistoryTitle.value = '';
    showNewHistoryDialog.value = false;
    await loadHistories(); // Reload histories
  } catch (error) {
    console.error('Failed to create history:', error);
  }
};

const editHistory = (history) => {
  if (!history.id) {
    console.error('History object missing ID:', history);
    return;
  }
  
  editingHistory.value = history;
  editHistoryTitle.value = history.title;
  showEditHistoryDialog.value = true;
};

const confirmEditHistory = async () => {
  if (!editHistoryTitle.value.trim() || !editingHistory.value) {
    return;
  }
  
  if (!editingHistory.value.id) {
    console.error('History object missing ID:', editingHistory.value);
    return;
  }
  
  try {
    await chatService.updateHistory(props.sessionId, editingHistory.value.id, {
      title: editHistoryTitle.value.trim()
    });
    editHistoryTitle.value = '';
    editingHistory.value = null;
    showEditHistoryDialog.value = false;
    await loadHistories(); // Reload histories
  } catch (error) {
    console.error('Failed to update history:', error);
  }
};

const deleteHistory = async (historyId) => {
  try {
    await chatService.deleteHistory(props.sessionId, historyId);
    await loadHistories(); // Reload histories
  } catch (error) {
    console.error('Failed to delete history:', error);
  }
};
</script>

<style scoped>
.history-panel {
  min-height: 300px;
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
  background-color: var(--surface-100);
}
</style>
