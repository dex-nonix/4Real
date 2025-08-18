<!-- ToolExecutionDialog.vue -->
<template>
  <Dialog 
    v-model:visible="dialogVisible" 
    :header="`Configure Tool: ${selectedTool}`" 
    modal 
    :style="{ width: '500px' }"
  >
    <div v-if="selectedTool" class="tool-form">
      <!-- Dynamic form based on tool type -->
      <div class="mb-3">
        <label class="block text-900 font-medium mb-2">Tool Parameters</label>
        
        <!-- Artist tools -->
        <div v-if="selectedTool.startsWith('artist:')" class="space-y-3">
          <div v-if="selectedTool === 'artist:get_info'">
            <label class="block text-700 text-sm mb-1">Artist ID</label>
            <InputText 
              v-model="toolFormData.artist_id" 
              placeholder="Enter artist ID (e.g., 1)" 
              class="w-full"
              type="number"
            />
          </div>
          <div v-if="selectedTool === 'artist:list_albums'">
            <label class="block text-700 text-sm mb-1">Artist ID</label>
            <InputText 
              v-model="toolFormData.artist_id" 
              placeholder="Enter artist ID (e.g., 1)" 
              class="w-full"
              type="number"
            />
            <label class="block text-700 text-sm mb-1 mt-2">Page</label>
            <InputText 
              v-model="toolFormData.page" 
              placeholder="Page number (default: 1)" 
              class="w-full"
              type="number"
            />
            <label class="block text-700 text-sm mb-1 mt-2">Page Size</label>
            <InputText 
              v-model="toolFormData.page_size" 
              placeholder="Items per page (default: 20)" 
              class="w-full"
              type="number"
            />
          </div>
        </div>

        <!-- Album tools -->
        <div v-if="selectedTool.startsWith('album:')" class="space-y-3">
          <div v-if="selectedTool === 'album:get_info'">
            <label class="block text-700 text-sm mb-1">Album ID</label>
            <InputText 
              v-model="toolFormData.album_id" 
              placeholder="Enter album ID" 
              class="w-full"
              type="number"
            />
          </div>
          <div v-if="selectedTool === 'album:list_tracks'">
            <label class="block text-700 text-sm mb-1">Album ID</label>
            <InputText 
              v-model="toolFormData.album_id" 
              placeholder="Enter album ID" 
              class="w-full"
              type="number"
            />
          </div>
        </div>

        <!-- File tools -->
        <div v-if="selectedTool.startsWith('file:')" class="space-y-3">
          <div v-if="selectedTool === 'file:list_artist_files'">
            <label class="block text-700 text-sm mb-1">Artist ID</label>
            <InputText 
              v-model="toolFormData.artist_id" 
              placeholder="Enter artist ID" 
              class="w-full"
              type="number"
            />
          </div>
          <div v-if="selectedTool === 'file:read_lyrics'">
            <label class="block text-700 text-sm mb-1">File ID</label>
            <InputText 
              v-model="toolFormData.file_id" 
              placeholder="Enter file ID" 
              class="w-full"
              type="number"
            />
          </div>
        </div>

        <!-- Track tools -->
        <div v-if="selectedTool.startsWith('track:')" class="space-y-3">
          <div v-if="selectedTool === 'track:get_info'">
            <label class="block text-700 text-sm mb-1">Track ID</label>
            <InputText 
              v-model="toolFormData.track_id" 
              placeholder="Enter track ID" 
              class="w-full"
              type="number"
            />
          </div>
          <div v-if="selectedTool === 'track:list_by_album'">
            <label class="block text-700 text-sm mb-1">Album ID</label>
            <InputText 
              v-model="toolFormData.album_id" 
              placeholder="Enter album ID" 
              class="w-full"
              type="number"
            />
          </div>
        </div>

        <!-- Style tools -->
        <div v-if="selectedTool.startsWith('style:')" class="space-y-3">
          <div v-if="selectedTool === 'style:list_all'">
            <p class="text-500 text-sm">No parameters needed for this tool.</p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-content-end gap-2">
        <Button 
          label="Cancel" 
          severity="secondary" 
          @click="closeDialog"
        />
        <Button 
          label="Execute Tool" 
          severity="primary" 
          @click="executeTool"
          :disabled="!selectedTool"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, defineExpose, defineEmits } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

// Props
const props = defineProps({
  selectedTool: { type: String, required: false, default: null }
});

// Emits
const emit = defineEmits(['execute-tool']);

// Reactive state for dialog visibility
const dialogVisible = ref(false);
const toolFormData = ref({});

// Functions to control the dialog
const openDialog = (toolName) => {
  toolFormData.value = {};
  dialogVisible.value = true;
};

const closeDialog = () => {
  dialogVisible.value = false;
  toolFormData.value = {};
};

const executeTool = () => {
  emit('execute-tool', {
    tool: props.selectedTool,
    args: toolFormData.value
  });
  closeDialog();
};

// Expose functions to the parent component
defineExpose({
  openDialog,
  closeDialog
});
</script>

<style scoped>
.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mb-1 {
  margin-bottom: 0.25rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.block {
  display: block;
}

.w-full {
  width: 100%;
}
</style>
