<template>
  <Dialog
      :visible="visible"
      @update:visible="updateVisible"
      modal
      header="Chat History"
      :style="{ width: '600px' }"
  >
    <div class="history-panel">
      <div class="flex justify-content-between align-items-center mb-3">
        <h3 class="m-0">Conversation History</h3>
        <Button
            icon="pi pi-plus"
            size="small"
            @click="createNewHistory"
            :disabled="!sessionId"
            v-tooltip.bottom="'New History'"
        />
      </div>

      <div v-if="!sessionId" class="flex justify-content-center p-4">
        <span class="text-500">Please select a session to view history</span>
      </div>

      <NxDynamicTable
          v-else
          :config="tableConfig"
          :data="histories"
          :loading="loading"
          @row-action="handleRowAction"
          @row-select="handleRowSelect"
      />
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
        <Button label="Cancel" text @click="showNewHistoryDialog = false"/>
        <Button label="Create" @click="confirmCreateHistory"/>
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
        <Button label="Cancel" text @click="showEditHistoryDialog = false"/>
        <Button label="Save" @click="confirmEditHistory"/>
      </template>
    </Dialog>
  </Dialog>
</template>

<script setup>
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import NxDynamicTable from '@nonix-dynamic/table/NxDynamicTable.vue';
import {inject, ref, watch, computed} from 'vue';

const props = defineProps({
  visible: {type: Boolean, required: true},
  sessionId: {type: [String, Number, null], required: false, default: null},
  currentHistoryId: {type: [String, Number, null], required: false, default: null}
});

const emit = defineEmits(['update:visible', 'historySelected', 'createHistory', 'updateHistory', 'deleteHistory']);

// Service - injected singleton
const chatService = inject('chat-service');

// State
const histories = ref([]);
const loading = ref(false);
const currentHistoryId = ref(props.currentHistoryId);

// Dialog states
const showNewHistoryDialog = ref(false);
const showEditHistoryDialog = ref(false);
const newHistoryTitle = ref('');
const editHistoryTitle = ref('');
const editingHistory = ref(null);

// Delete confirmation states
const deletingHistoryId = ref(null);

// Table configuration
const tableConfig = computed(() => ({
  columns: [
    { field: 'title', header: 'Title', sortable: true },
    { field: 'message_count', header: 'Messages', sortable: true }
  ],
  actions: ['edit', 'delete'],
  actionsDisplay: 'icons-only',
  sortable: true,
  striped: true,
  hover: true,
  paginated: false
}));

// Load histories when dialog opens
const loadHistories = async () => {
  if (!props.sessionId) {
    console.log('No session ID provided, skipping history load');
    histories.value = [];
    return;
  }

  try {
    loading.value = true;
    const response = await chatService.getHistories(props.sessionId);

    histories.value = response.data || [];
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
  } else if (newVisible && !props.sessionId) {
    console.log('Dialog opened but no session ID, showing empty state');
    histories.value = [];
  }
});

// Watch for currentHistoryId changes to update selection
watch(() => props.currentHistoryId, (newId) => {
  currentHistoryId.value = newId;
}, { immediate: true });

const updateVisible = (value) => {
  emit('update:visible', value);
};

const close = () => {
  emit('update:visible', false);
};

const selectHistory = async (historyId) => {
  try {
    await chatService.selectHistory(props.sessionId, historyId);
    currentHistoryId.value = historyId;
    emit('historySelected', historyId);
    close();
  } catch (error) {
    console.error('Failed to select history:', error);
  }
};

const handleRowSelect = (event) => {
  if (event.data && event.data.id) {
    selectHistory(event.data.id);
  }
};

const handleRowAction = ({ action, rowData }) => {
  switch (action) {
    case 'edit':
      editHistory(rowData);
      break;
    case 'delete':
      startDelete(rowData.id);
      break;
  }
};

const createNewHistory = () => {
  if (!props.sessionId) {
    console.warn('Cannot create history: no session ID');
    return;
  }
  showNewHistoryDialog.value = true;
};

const confirmCreateHistory = async () => {
  if (!props.sessionId) {
    console.warn('Cannot create history: no session ID');
    return;
  }

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

const startDelete = (historyId) => {
  deletingHistoryId.value = historyId;
};

const cancelDelete = () => {
  deletingHistoryId.value = null;
};

const confirmDelete = async (historyId) => {
  try {
    await chatService.deleteHistory(props.sessionId, historyId);
    deletingHistoryId.value = null;
    await loadHistories(); // Reload histories
    
    // If we deleted the current history, select another one
    if (currentHistoryId.value === historyId) {
      if (histories.value.length > 0) {
        // Select the first available history
        const newHistoryId = histories.value[0].id;
        currentHistoryId.value = newHistoryId;
        emit('historySelected', newHistoryId);
      } else {
        // No histories left, emit null
        currentHistoryId.value = null;
        emit('historySelected', null);
      }
    }
  } catch (error) {
    console.error('Failed to delete history:', error);
    deletingHistoryId.value = null;
  }
};
</script>

<style scoped>
.history-panel {
  min-height: 300px;
}

.tiny-button {
  width: 24px !important;
  height: 24px !important;
  min-width: 24px !important;
  padding: 0 !important;
}
</style>
