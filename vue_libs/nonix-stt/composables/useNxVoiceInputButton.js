import { ref, computed, watch, inject, onUnmounted } from 'vue';

export function useNxVoiceInputButton() {
  const sttService = inject('stt-configurations');
  
  // State
  const selectedMethod = ref('native');
  const selectedConfig = ref(null);
  const configurations = ref([]);
  const loading = ref(false);
  const error = ref(null);
  
  // WebSocket connection for backend STT
  const socket = ref(null);
  const connectionId = ref(null);
  const isConnected = ref(false);
  const isStreaming = ref(false);
  
  // Computed
  const isBackendMethod = computed(() => selectedMethod.value === 'backend');
  const isNativeMethod = computed(() => selectedMethod.value === 'native');
  const canStartStreaming = computed(() => 
    isBackendMethod.value && selectedConfig.value && isConnected.value && !isStreaming.value
  );
  
  // Load configurations
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
  
  // Set configuration
  const setConfiguration = (config) => {
    selectedMethod.value = config.method;
    selectedConfig.value = config.config;
  };
  
  // WebSocket connection management
  const connectWebSocket = () => {
    if (socket.value) return;
    
    // Get socket from global app instance
    const app = getCurrentInstance()?.appContext?.app;
    if (!app?.config?.globalProperties?.$socket) {
      console.error('Socket.IO not available');
      return;
    }
    
    socket.value = app.config.globalProperties.$socket;
    connectionId.value = generateConnectionId();
    
    // Register event listeners
    socket.value.on('stt_connected', handleConnected);
    socket.value.on('stt_streaming_started', handleStreamingStarted);
    socket.value.on('stt_transcription', handleTranscription);
    socket.value.on('stt_streaming_stopped', handleStreamingStopped);
    socket.value.on('stt_error', handleError);
    
    // Connect
    socket.value.emit('stt_connect');
  };
  
  const disconnectWebSocket = () => {
    if (socket.value) {
      socket.value.emit('stt_disconnect');
      socket.value.off('stt_connected', handleConnected);
      socket.value.off('stt_streaming_started', handleStreamingStarted);
      socket.value.off('stt_transcription', handleTranscription);
      socket.value.off('stt_streaming_stopped', handleStreamingStopped);
      socket.value.off('stt_error', handleError);
      socket.value = null;
    }
    isConnected.value = false;
    isStreaming.value = false;
    connectionId.value = null;
  };
  
  // WebSocket event handlers
  const handleConnected = (data) => {
    isConnected.value = true;
    console.log('STT WebSocket connected:', data);
  };
  
  const handleStreamingStarted = (data) => {
    isStreaming.value = true;
    console.log('STT streaming started:', data);
  };
  
  const handleTranscription = (data) => {
    // This will be handled by the parent component
    console.log('STT transcription received:', data);
  };
  
  const handleStreamingStopped = (data) => {
    isStreaming.value = false;
    console.log('STT streaming stopped:', data);
  };
  
  const handleError = (data) => {
    error.value = data.error;
    isStreaming.value = false;
    console.error('STT error:', data);
  };
  
  // Voice input methods
  const startRecording = () => {
    if (isNativeMethod.value) {
      // Use native browser STT - this will be handled by NxVoiceInputButton
      return;
    }
    
    if (isBackendMethod.value) {
      if (!isConnected.value) {
        connectWebSocket();
        return;
      }
      
      if (canStartStreaming.value) {
        socket.value.emit('stt_start_streaming', {
          connection_id: connectionId.value,
          config_id: selectedConfig.value.id
        });
      }
    }
  };
  
  const stopRecording = () => {
    if (isNativeMethod.value) {
      // Use native browser STT - this will be handled by NxVoiceInputButton
      return;
    }
    
    if (isBackendMethod.value && isStreaming.value) {
      socket.value.emit('stt_stop_streaming', {
        connection_id: connectionId.value
      });
    }
  };
  
  const sendAudioChunk = (audioData) => {
    if (isBackendMethod.value && isStreaming.value && socket.value) {
      socket.value.emit('stt_audio_chunk', {
        connection_id: connectionId.value,
        audio_data: audioData
      });
    }
  };
  
  // Utility functions
  const generateConnectionId = () => {
    return 'stt_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  };
  
  const getCurrentInstance = () => {
    // This would need to be imported from Vue in a real implementation
    return null;
  };
  
  // Cleanup
  const cleanup = () => {
    disconnectWebSocket();
  };
  
  // Auto-connect when backend method is selected
  watch(isBackendMethod, (newValue) => {
    if (newValue) {
      connectWebSocket();
    } else {
      disconnectWebSocket();
    }
  });
  
  // Auto-disconnect on unmount
  onUnmounted(() => {
    cleanup();
  });
  
  return {
    // State
    selectedMethod,
    selectedConfig,
    configurations,
    loading,
    error,
    isConnected,
    isStreaming,
    
    // Computed
    isBackendMethod,
    isNativeMethod,
    canStartStreaming,
    
    // Methods
    loadConfigurations,
    setConfiguration,
    startRecording,
    stopRecording,
    sendAudioChunk,
    connectWebSocket,
    disconnectWebSocket,
    cleanup
  };
}
