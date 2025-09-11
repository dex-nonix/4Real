<script setup>
import {computed, onMounted, onUnmounted, reactive} from 'vue';
import Button from 'primevue/button';

const props = defineProps({
  disabled: {type: Boolean, default: false},
  size: {type: String, default: 'normal'},
  variant: {type: String, default: 'primary'}
});

const emit = defineEmits([
  // Core Events
  'text',           // { text: string, confidence: number, isFinal: boolean }
  'interim-text',   // { text: string, confidence: number }

  // Status Events
  'recording-start',    // { timestamp: Date }
  'recording-stop',     // { timestamp: Date, duration: number }
  'recording-error',    // { error: string, code: string }

  // API Events
  'speech-start',       // { timestamp: Date }
  'speech-end',         // { timestamp: Date }
  'audio-start',        // { timestamp: Date }
  'audio-end',          // { timestamp: Date }
  'sound-start',        // { timestamp: Date }
  'sound-end',          // { timestamp: Date }
  'no-speech',          // { timestamp: Date }
  'no-match',           // { timestamp: Date }

  // System Events
  'permission-denied',  // { timestamp: Date }
  'permission-granted', // { timestamp: Date }
  'not-supported',      // { browser: string, version: string }
]);

// State Management - Simple reactive object
const state = reactive({
  isRecording: false,
  isSupported: false,
  recognition: null,
  error: null,
  permissionGranted: false,
  recordingStartTime: null,
  browser: '',
  version: ''
});

// Computed Properties
const buttonIcon = computed(() => {
  if (state.error) return 'pi pi-exclamation-triangle';
  if (state.isRecording) return 'pi pi-stop-circle';
  return 'pi pi-microphone';
});

const buttonSeverity = computed(() => {
  if (state.error) return 'danger';
  if (state.isRecording) return 'danger';
  return props.variant;
});

const buttonSize = computed(() => {
  switch (props.size) {
    case 'small':
      return 'p-button-sm';
    case 'large':
      return 'p-button-lg';
    default:
      return '';
  }
});

const isButtonDisabled = computed(() => {
  return props.disabled || !state.isSupported;
});

const buttonTooltip = computed(() => {
  if (!state.isSupported) return 'Voice input not supported in this browser';
  if (state.error) return `Error: ${state.error}`;
  if (state.isRecording) return 'Click to stop recording';
  return 'Click to start voice input';
});

// Browser Support Detection
const checkBrowserSupport = () => {
  const userAgent = navigator.userAgent;
  const browserMatch = userAgent.match(/(Chrome|Firefox|Safari|Edge|Opera)\/(\d+)/);
  state.browser = browserMatch ? browserMatch[1] : 'Unknown';
  state.version = browserMatch ? browserMatch[2] : 'Unknown';

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    state.isSupported = false;
    emit('not-supported', {
      browser: state.browser,
      version: state.version,
      timestamp: new Date()
    });
    return false;
  }

  state.isSupported = true;
  return true;
};

// Create Recognition - Match working React approach
const createRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  // Match the working React settings
  recognition.maxAlternatives = 10;
  // Don't set continuous or interimResults - use defaults (false)

  return recognition;
};

// Event Handlers - Complete set
const handleStart = () => {
  state.recordingStartTime = new Date();
  state.isRecording = true;
  state.error = null;
  emit('recording-start', {timestamp: state.recordingStartTime});
};

const handleEnd = () => {
  const endTime = new Date();
  const duration = state.recordingStartTime ?
      endTime.getTime() - state.recordingStartTime.getTime() : 0;

  state.isRecording = false;
  emit('recording-stop', {
    timestamp: endTime,
    duration: duration
  });
  state.recognition = null; // Clean up
};

const handleResult = (event) => {
  let finalTranscript = '';
  let interimTranscript = '';

  for (let i = event.resultIndex; i < event.results.length; i++) {
    const result = event.results[i];
    const transcript = result[0].transcript;
    const confidence = result[0].confidence;

    if (result.isFinal) {
      finalTranscript += transcript;
      emit('text', {
        text: transcript,
        confidence: confidence,
        isFinal: true,
        timestamp: new Date()
      });
    } else {
      interimTranscript += transcript;
      emit('interim-text', {
        text: transcript,
        confidence: confidence,
        timestamp: new Date()
      });
    }
  }
};

const handleError = (event) => {
  state.error = event.message || event.error;
  state.isRecording = false;

  emit('recording-error', {
    error: event.message || event.error,
    code: event.error,
    timestamp: new Date()
  });
  state.recognition = null;
};

// Additional Event Handlers
const handleAudioStart = () => {
  emit('audio-start', {timestamp: new Date()});
};

const handleAudioEnd = () => {
  emit('audio-end', {timestamp: new Date()});
};

const handleSoundStart = () => {
  emit('sound-start', {timestamp: new Date()});
};

const handleSoundEnd = () => {
  emit('sound-end', {timestamp: new Date()});
};

const handleSpeechStart = () => {
  emit('speech-start', {timestamp: new Date()});
};

const handleSpeechEnd = () => {
  emit('speech-end', {timestamp: new Date()});
};

const handleNoSpeech = () => {
  emit('no-speech', {timestamp: new Date()});
};

const handleNoMatch = () => {
  emit('no-match', {timestamp: new Date()});
};

// Public Methods - Complete feature set
const startRecording = () => {
  if (!state.isSupported) {
    emit('recording-error', {
      error: 'Speech recognition not supported',
      code: 'NOT_SUPPORTED'
    });
    return;
  }

  try {
    state.recognition = createRecognition();

    // Bind all event handlers
    state.recognition.onstart = handleStart;
    state.recognition.onend = handleEnd;
    state.recognition.onresult = handleResult;
    state.recognition.onerror = handleError;
    state.recognition.onaudiostart = handleAudioStart;
    state.recognition.onaudioend = handleAudioEnd;
    state.recognition.onsoundstart = handleSoundStart;
    state.recognition.onsoundend = handleSoundEnd;
    state.recognition.onspeechstart = handleSpeechStart;
    state.recognition.onspeechend = handleSpeechEnd;
    state.recognition.onnospeech = handleNoSpeech;
    state.recognition.onnomatch = handleNoMatch;

    state.recognition.start();
  } catch (error) {
    state.isRecording = false;
    state.recognition = null;
    emit('recording-error', {
      error: error.message || 'Failed to start recording',
      code: 'START_ERROR',
      timestamp: new Date()
    });
  }
};

const stopRecording = () => {
  if (state.recognition) {
    try {
      state.recognition.stop();
    } catch (error) {
      // Ignore stop errors
    }
    state.recognition = null;
  }
  state.isRecording = false;
};

const toggleRecording = () => {
  if (state.isRecording) {
    stopRecording();
  } else {
    startRecording();
  }
};

const cleanup = () => {
  if (state.recognition) {
    try {
      state.recognition.stop();
    } catch (error) {
      // Ignore cleanup errors
    }
    state.recognition = null;
  }
  state.isRecording = false;
  state.error = null;
};

// Lifecycle
onMounted(() => {
  checkBrowserSupport();
});

onUnmounted(() => {
  cleanup();
});

// Expose methods and computed properties
defineExpose({
  startRecording,
  stopRecording,
  toggleRecording,
  cleanup,
  isSupported: computed(() => state.isSupported),
  isRecording: computed(() => state.isRecording),
  permissionGranted: computed(() => state.permissionGranted)
});
</script>

<template>
  <Button
      :icon="buttonIcon"
      :severity="buttonSeverity"
      :class="['voice-input-btn', {
      'recording': state.isRecording,
      'error': !!state.error,
      'unsupported': !state.isSupported
    }]"
      :disabled="isButtonDisabled"
      :rounded="true"
      style="width: 24px; height: 24px;"
      @click="toggleRecording"
      v-tooltip="buttonTooltip"
      :aria-label="state.isRecording ? 'Stop voice recording' : 'Start voice recording'"
  />
</template>

<style scoped>
/* Minimal styling - let PrimeVue handle the rest */

.voice-input-btn.recording {
  animation: pulse-red 0.6s ease-in-out infinite alternate;
}

.voice-input-btn.error {
  animation: shake 0.5s ease-in-out;
}

@keyframes pulse-red {
  from {
    box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7);
  }
  to {
    box-shadow: 0 0 0 4px rgba(255, 59, 48, 0);
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-1px);
  }
  75% {
    transform: translateX(1px);
  }
}
</style>
