<script setup>
import { ref, computed, onMounted, inject } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import RadioButton from 'primevue/radiobutton';
import Card from 'primevue/card';
import Badge from 'primevue/badge';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';

const props = defineProps({
  visible: { type: Boolean, default: false }
});

const emit = defineEmits(['update:visible', 'config-selected']);

const sttService = inject('stt-configurations');

const selectedMethod = ref('native');
const selectedConfigId = ref(null);
const configurations = ref([]);
const loading = ref(false);
const error = ref(null);

const availableMethods = [
  {
    id: 'native',
    name: 'Browser Native',
    description: 'Uses your browser\'s built-in speech recognition',
    icon: 'pi pi-microphone',
    badge: 'Fast'
  },
  {
    id: 'backend',
    name: 'Backend STT',
    description: 'Uses server-side Whisper models for better accuracy',
    icon: 'pi pi-server',
    badge: 'Accurate'
  }
];

const activeConfigurations = computed(() => 
  configurations.value.filter(config => config.is_active)
);

const selectedConfig = computed(() => 
  activeConfigurations.value.find(config => config.id === selectedConfigId.value)
);

const canSave = computed(() => {
  if (selectedMethod.value === 'native') return true;
  return selectedMethod.value === 'backend' && selectedConfigId.value !== null;
});

const loadConfigurations = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await sttService.getAll({ filters: { is_active: true } });
    configurations.value = response.data || [];
  } catch (err) {
    error.value = 'Failed to load STT configurations';
    console.error('Error loading configurations:', err);
  } finally {
    loading.value = false;
  }
};

const handleSave = () => {
  const config = selectedMethod.value === 'native' 
    ? { method: 'native', config: null }
    : { method: 'backend', config: selectedConfig.value };
  
  emit('config-selected', config);
  emit('update:visible', false);
};

const handleCancel = () => {
  emit('update:visible', false);
};

const getConfigBadge = (config) => {
  if (config.whisper_model === 'base') return 'Fast';
  if (config.whisper_model === 'small') return 'Balanced';
  if (config.whisper_model === 'medium') return 'Accurate';
  if (config.whisper_model === 'large') return 'Very Accurate';
  return 'Custom';
};

const getConfigSeverity = (config) => {
  if (config.whisper_model === 'base') return 'success';
  if (config.whisper_model === 'small') return 'info';
  if (config.whisper_model === 'medium') return 'warning';
  if (config.whisper_model === 'large') return 'danger';
  return 'secondary';
};

onMounted(() => {
  if (props.visible) {
    loadConfigurations();
  }
});

// Watch for dialog visibility changes
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    loadConfigurations();
  }
});
</script>

<template>
  <Dialog
    :visible="visible"
    @update:visible="emit('update:visible', $event)"
    modal
    header="Voice Input Settings"
    :style="{ width: '600px' }"
    :closable="true"
  >
    <div class="flex flex-column gap-4">
      <!-- Method Selection -->
      <div class="flex flex-column gap-3">
        <h4 class="m-0">Select Voice Input Method</h4>
        
        <div class="flex flex-column gap-3">
          <div 
            v-for="method in availableMethods" 
            :key="method.id"
            class="flex align-items-center gap-3 p-3 border-1 surface-border border-round cursor-pointer transition-colors transition-duration-150"
            :class="{ 'border-primary bg-primary-50': selectedMethod === method.id }"
            @click="selectedMethod = method.id"
          >
            <RadioButton 
              :value="method.id" 
              v-model="selectedMethod" 
              :inputId="method.id"
            />
            <label :for="method.id" class="flex-1 cursor-pointer">
              <div class="flex align-items-center gap-2 mb-1">
                <i :class="method.icon" class="text-primary"></i>
                <span class="font-semibold">{{ method.name }}</span>
                <Badge :value="method.badge" severity="info" size="small" />
              </div>
              <p class="text-sm text-color-secondary m-0">{{ method.description }}</p>
            </label>
          </div>
        </div>
      </div>

      <!-- Backend Configuration Selection -->
      <div v-if="selectedMethod === 'backend'" class="flex flex-column gap-3">
        <h4 class="m-0">Select STT Configuration</h4>
        
        <div v-if="loading" class="flex justify-content-center p-4">
          <ProgressSpinner size="small" />
        </div>
        
        <Message v-if="error" severity="error" :closable="false">
          {{ error }}
        </Message>
        
        <div v-if="!loading && !error" class="flex flex-column gap-2">
          <div 
            v-for="config in activeConfigurations" 
            :key="config.id"
            class="flex align-items-center gap-3 p-3 border-1 surface-border border-round cursor-pointer transition-colors transition-duration-150"
            :class="{ 'border-primary bg-primary-50': selectedConfigId === config.id }"
            @click="selectedConfigId = config.id"
          >
            <RadioButton 
              :value="config.id" 
              v-model="selectedConfigId" 
              :inputId="`config-${config.id}`"
            />
            <label :for="`config-${config.id}`" class="flex-1 cursor-pointer">
              <div class="flex align-items-center gap-2 mb-1">
                <span class="font-semibold">{{ config.name }}</span>
                <Badge 
                  :value="getConfigBadge(config)" 
                  :severity="getConfigSeverity(config)" 
                  size="small" 
                />
              </div>
              <div class="text-sm text-color-secondary">
                <div>Model: {{ config.whisper_model }}</div>
                <div>Device: {{ config.device }}</div>
                <div v-if="config.language">Language: {{ config.language }}</div>
                <div>Sample Rate: {{ config.sample_rate }}Hz</div>
              </div>
            </label>
          </div>
          
          <div v-if="activeConfigurations.length === 0" class="text-center p-4 text-color-secondary">
            No active STT configurations available
          </div>
        </div>
      </div>

      <!-- Selected Configuration Preview -->
      <div v-if="selectedConfig" class="p-3 bg-primary-50 border-1 border-primary border-round">
        <h5 class="m-0 mb-2">Selected Configuration</h5>
        <div class="text-sm">
          <div><strong>Name:</strong> {{ selectedConfig.name }}</div>
          <div><strong>Model:</strong> {{ selectedConfig.whisper_model }}</div>
          <div><strong>Device:</strong> {{ selectedConfig.device }}</div>
          <div v-if="selectedConfig.language"><strong>Language:</strong> {{ selectedConfig.language }}</div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-content-end gap-2">
        <Button 
          label="Cancel" 
          severity="secondary" 
          @click="handleCancel"
        />
        <Button 
          label="Save" 
          :disabled="!canSave"
          @click="handleSave"
        />
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
.transition-colors {
  transition: all 0.15s ease;
}

.transition-colors:hover {
  background-color: var(--surface-50);
}
</style>
