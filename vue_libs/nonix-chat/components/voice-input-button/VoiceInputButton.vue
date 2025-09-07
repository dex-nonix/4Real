<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import Button from 'primevue/button';

const props = defineProps({
  // Core Configuration
  disabled: { type: Boolean, default: false },
  language: { type: String, default: 'en-US' },
  continuous: { type: Boolean, default: false },
  interimResults: { type: Boolean, default: true },

  // Visual Customization
  size: { type: String, default: 'normal' }, // 'small', 'normal', 'large'
  variant: { type: String, default: 'primary' }, // 'primary', 'secondary', 'danger'

  // Advanced Options
  maxAlternatives: { type: Number, default: 1 },
  serviceURI: { type: String, default: null },
  grammars: { type: Array, default: () => [] }
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

// State Management
const state = reactive({
  isRecording: false,
  isSupported: false,
  isProcessing: false,
  recognition: null,
  currentText: '',
  error: null,
  permissionGranted: false,
  recordingStartTime: null,
  browser: '',
  version: '',
  captureStream: null,
  audioContext: null,
  triedAudioCaptureRetry: false 
});

// Computed Properties
const buttonIcon = computed(() => {
  if (state.error) return 'pi pi-exclamation-triangle';
  if (state.isProcessing) return 'pi pi-spin pi-spinner';
  if (state.isRecording) return 'pi pi-stop-circle';
  return 'pi pi-microphone';
});

const buttonSeverity = computed(() => {
  if (state.error) return 'danger';
  if (state.isRecording) return 'danger';
  if (state.isProcessing) return 'warning';
  return props.variant;
});

const buttonSize = computed(() => {
  switch (props.size) {
    case 'small': return 'p-button-sm';
    case 'large': return 'p-button-lg';
    default: return '';
  }
});

const isButtonDisabled = computed(() => {
  return props.disabled || !state.isSupported || state.isProcessing;
});

const buttonTooltip = computed(() => {
  if (!state.isSupported) return 'Voice input not supported in this browser';
  if (state.error) return `Error: ${state.error}`;
  if (state.isRecording) return 'Click to stop recording';
  if (state.isProcessing) return 'Processing speech...';
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

// Permission Handling
const getAnyMicStream = async () => {
  const devices = await navigator.mediaDevices.enumerateDevices();
  const mics = devices.filter(d => d.kind === 'audioinput');
  if (mics.length === 0) throw new Error('No audioinput devices');
  const deviceId = mics[0].deviceId;
  return navigator.mediaDevices.getUserMedia({ audio: { deviceId } });
};
const requestMicrophonePermission = async () => {
  try {
    let stream = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      if (e && (e.name === 'NotFoundError' || e.name === 'OverconstrainedError')) {
        stream = await getAnyMicStream();
      } else {
        throw e;
      }
    }
    stream.getTracks().forEach(track => track.stop());
    state.permissionGranted = true;
    emit('permission-granted', { timestamp: new Date() });
  } catch (error) {
    state.permissionGranted = false;
    const name = error && error.name ? error.name : 'Error';
    if (name === 'NotAllowedError' || name === 'SecurityError') {
      emit('permission-denied', { timestamp: new Date() });
      handleError('permission-denied', error.message || 'Microphone permission denied');
      return;
    }
    if (name === 'NotFoundError') {
      handleError('device-not-found', error.message || 'No microphone device found');
      return;
    }
    if (name === 'NotReadableError') {
      handleError('not-readable', error.message || 'Microphone not readable');
      return;
    }
    handleError('mic-error', error.message || String(error));
  }
};

const ensureAudioReady = async () => {
  if (!state.audioContext) {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (Ctx) state.audioContext = new Ctx();
  }
  if (state.audioContext && state.audioContext.state === 'suspended') {
    await state.audioContext.resume();
  }
};

const primeAudioCapture = async () => {
  if (state.captureStream) return;
  state.captureStream = await navigator.mediaDevices.getUserMedia({ audio: true });
};

const releaseAudioCapture = () => {
  if (state.captureStream) {
    try {
      state.captureStream.getTracks().forEach(t => t.stop());
    } catch (_) {}
    state.captureStream = null;
  }
};

// Speech Recognition Setup
const createRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  // Configure recognition
  recognition.lang = props.language;
  recognition.continuous = props.continuous;
  recognition.interimResults = props.interimResults;
  recognition.maxAlternatives = props.maxAlternatives;

  if (props.serviceURI) {
    recognition.serviceURI = props.serviceURI;
  }

  if (props.grammars.length > 0) {
    const grammarList = new (window.SpeechGrammarList || window.webkitSpeechGrammarList)();
    props.grammars.forEach(grammar => grammarList.addFromString(grammar, 1));
    recognition.grammars = grammarList;
  }

  return recognition;
};

// Event Handlers
const handleStart = () => {
  state.recordingStartTime = new Date();
  state.isRecording = true;
  state.error = null;
  emit('recording-start', { timestamp: state.recordingStartTime });
};

const handleEnd = () => {
  const endTime = new Date();
  const duration = state.recordingStartTime ?
    endTime.getTime() - state.recordingStartTime.getTime() : 0;

  state.isRecording = false;
  state.isProcessing = false;
  emit('recording-stop', {
    timestamp: endTime,
    duration: duration
  });
  releaseAudioCapture();
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

  state.currentText = finalTranscript || interimTranscript;
};

const handleError = (errorCode, errorMessage) => {
  state.error = errorMessage;
  state.isRecording = false;
  state.isProcessing = false;

  emit('recording-error', {
    error: errorMessage,
    code: errorCode,
    timestamp: new Date()
  });
};

const handleAudioStart = () => {
  emit('audio-start', { timestamp: new Date() });
};

const handleAudioEnd = () => {
  emit('audio-end', { timestamp: new Date() });
  releaseAudioCapture();
};

const handleSoundStart = () => {
  emit('sound-start', { timestamp: new Date() });
};

const handleSoundEnd = () => {
  emit('sound-end', { timestamp: new Date() });
};

const handleSpeechStart = () => {
  emit('speech-start', { timestamp: new Date() });
};

const handleSpeechEnd = () => {
  emit('speech-end', { timestamp: new Date() });
};

const handleNoSpeech = () => {
  emit('no-speech', { timestamp: new Date() });
};

const handleNoMatch = () => {
  emit('no-match', { timestamp: new Date() });
};

// Public Methods
const startRecording = async () => {
  if (!state.isSupported) {
    handleError('not-supported', 'Speech recognition not supported');
    return;
  }

  if (!state.permissionGranted) {
    await requestMicrophonePermission();
    if (!state.permissionGranted) return;
  }

  try {
    state.isProcessing = true;
    state.triedAudioCaptureRetry = false;
    await ensureAudioReady();
    await primeAudioCapture();
    await new Promise(r => setTimeout(r, 200));
    state.recognition = createRecognition();

    // Bind event handlers
    state.recognition.onstart = handleStart;
    state.recognition.onend = handleEnd;
    state.recognition.onresult = handleResult;
    state.recognition.onerror = async (event) => {
      if (event && event.error === 'audio-capture' && !state.triedAudioCaptureRetry) {
        state.triedAudioCaptureRetry = true;
        try {
          releaseAudioCapture();
          await ensureAudioReady();
          await primeAudioCapture();
          await new Promise(r => setTimeout(r, 300));
          if (typeof state.recognition.abort === 'function') state.recognition.abort();
          state.recognition.start();
          return;
        } catch (_) {}
      }
      handleError(event.error, event.message);
    };
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
    handleError('start-failed', `Failed to start recording: ${error.message}`);
  }
};

const stopRecording = () => {
  if (state.recognition) {
    state.recognition.stop();
  }
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
      state.recognition = null;
    } catch (error) {
      // Ignore cleanup errors
    }
  }
  state.isRecording = false;
  state.isProcessing = false;
  state.error = null;
};

// Lifecycle
onMounted(() => {
  checkBrowserSupport();
});

onUnmounted(() => {
  cleanup();
});

// Expose methods for parent components
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
    :class="[buttonSize, 'voice-input-btn', {
      'recording': state.isRecording,
      'processing': state.isProcessing,
      'error': !!state.error,
      'unsupported': !state.isSupported
    }]"
    :disabled="isButtonDisabled"
    :text="false"
    :rounded="true"
    @click="toggleRecording"
    v-tooltip="buttonTooltip"
    :aria-label="state.isRecording ? 'Stop voice recording' : 'Start voice recording'"
  />
</template>

<style scoped>
.voice-input-btn {
  transition: all 0.2s ease;
  position: relative;
  min-width: 2.5rem;
  height: 2.5rem;
}

.voice-input-btn:not(.p-disabled):hover {
  transform: scale(1.05);
}

.voice-input-btn.recording {
  animation: pulse-red 1.5s infinite;
  box-shadow: 0 0 15px rgba(255, 59, 48, 0.6);
}

.voice-input-btn.processing {
  animation: spin 1s linear infinite;
}

.voice-input-btn.error {
  animation: shake 0.5s ease-in-out;
}

.voice-input-btn.unsupported {
  opacity: 0.5;
}

.voice-input-btn.unsupported:not(.p-disabled):hover {
  transform: none;
  cursor: not-allowed;
}

/* Size variants */
.voice-input-btn.p-button-sm {
  min-width: 2rem;
  height: 2rem;
}

.voice-input-btn.p-button-lg {
  min-width: 3rem;
  height: 3rem;
}

/* Animations */
@keyframes pulse-red {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 10px rgba(255, 59, 48, 0.4);
  }
  50% {
    transform: scale(1.08);
    box-shadow: 0 0 20px rgba(255, 59, 48, 0.8);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-2px); }
  75% { transform: translateX(2px); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .voice-input-btn.recording {
    box-shadow: 0 0 15px rgba(255, 69, 58, 0.6);
  }

  .voice-input-btn.recording {
    box-shadow: 0 0 20px rgba(255, 69, 58, 0.8);
  }
}

/* Focus styles for accessibility */
.voice-input-btn:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .voice-input-btn {
    border: 2px solid currentColor;
  }

  .voice-input-btn.recording {
    border-color: #ff3b30;
  }
}
</style>
