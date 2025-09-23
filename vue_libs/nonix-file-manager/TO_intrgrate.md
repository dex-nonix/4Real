

## **ENHANCED BLUEPRINT: Context-Aware Maximize in NxFileView**

### **NxFileView Component - Built-in Maximize Logic**

```vue
<template>
  <div class="file-view" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- Image Preview with Overlay Maximize Button -->
    <div v-if="isImage && previewUrl" class="image-preview-container">
      <img :src="previewUrl" :alt="selectedFile.title || selectedFile.original_filename" 
           :style="imageStyle" />
      
      <!-- Overlay Maximize Button -->
      <Button 
        icon="pi pi-expand" 
        class="maximize-overlay-btn"
        text 
        rounded 
        size="small"
        v-tooltip="maximizeTooltip"
        @click="handleMaximize"
      />
    </div>

    <!-- Audio Preview -->
    <div v-else-if="isAudio && previewUrl" class="audio-preview">
      <audio :src="previewUrl" controls :style="mediaStyle"></audio>
    </div>

    <!-- Video Preview with Overlay -->
    <div v-else-if="isVideo && previewUrl" class="video-preview-container">
      <video :src="previewUrl" controls :style="mediaStyle"></video>
      
      <!-- Overlay Maximize Button -->
      <Button 
        icon="pi pi-expand" 
        class="maximize-overlay-btn"
        text 
        rounded 
        size="small"
        v-tooltip="maximizeTooltip"
        @click="handleMaximize"
      />
    </div>

    <!-- File Icon for other types -->
    <div v-else class="file-icon-preview">
      <NxFilePreview :value="selectedFile" :showSize="true" :showCategory="true" 
                    :style="{ fontSize: isFullscreen ? '5rem' : '3rem' }" />
    </div>

    <!-- File Details & Actions -->
    <!-- ... existing content ... -->
  </div>
</template>

<script setup>
const props = defineProps({
  selectedFile: { type: Object, required: true },
  maximizeMode: { 
    type: String, 
    default: 'dialog', // 'dialog' or 'fullscreen'
    validator: value => ['dialog', 'fullscreen'].includes(value)
  }
})

// Maximize mode determines behavior:
// - 'dialog': maximize opens NxFileViewDialog (for sidebar use)
// - 'fullscreen': maximize toggles true fullscreen (for dialog use)

const isFullscreen = ref(false)

const imageStyle = computed(() => ({
  maxWidth: '100%',
  maxHeight: isFullscreen ? '80vh' : '200px',
  objectFit: 'contain'
}))

const mediaStyle = computed(() => ({
  width: isFullscreen ? '100%' : 'auto',
  maxHeight: isFullscreen ? '70vh' : '200px'
}))

const maximizeTooltip = computed(() => {
  if (props.maximizeMode === 'dialog') {
    return 'Open in Fullscreen Dialog'
  }
  return isFullscreen.value ? 'Minimize' : 'Maximize to Full Browser'
})

const handleMaximize = () => {
  if (props.maximizeMode === 'dialog') {
    // Emit to open fullscreen dialog
    emit('open-fullscreen-dialog')
  } else {
    // Toggle fullscreen mode
    isFullscreen.value = !isFullscreen.value
  }
}
</script>

<style scoped>
.image-preview-container, .video-preview-container {
  position: relative;
}

.maximize-overlay-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.maximize-overlay-btn:hover {
  opacity: 1;
}

.fullscreen-mode {
  /* Styles for when component is in fullscreen mode */
}
</style>
```

### **Updated Component Usage**

#### **NxFilePreviewPane.vue** (Sidebar)
```vue
<template>
  <Card class="h-full">
    <NxFileView
      :selectedFile="selectedFile"
      :maximizeMode="'dialog'"  <!-- Opens fullscreen dialog -->
      @open-fullscreen-dialog="$emit('open-fullscreen-dialog')"
    />
  </Card>
</template>
```

#### **NxFileViewDialog.vue** (Dialog)
```vue
<template>
  <Dialog
    v-model:visible="visible"
    modal
    :header="selectedFile?.title || selectedFile?.original_filename || 'File View'"
    :style="dialogStyle"
    :closable="true"
    :maximizable="false"  <!-- We handle maximize ourselves -->
  >
    <NxFileView
      :selectedFile="selectedFile"
      :maximizeMode="'fullscreen'"  <!-- Toggles true fullscreen -->
      @open-fullscreen-dialog="/* already in dialog */"
    />
    
    <!-- Custom header with our maximize/minimize controls -->
    <template #header>
      <div class="flex justify-content-between align-items-center w-full">
        <span>{{ selectedFile.title || selectedFile.original_filename }}</span>
        <div class="flex gap-2">
          <Button 
            :icon="isFullscreen ? 'pi pi-minus' : 'pi pi-expand'" 
            size="small" 
            text 
            rounded 
            v-tooltip="isFullscreen ? 'Minimize' : 'Maximize'"
            @click="toggleFullscreen"
          />
          <Button 
            icon="pi pi-times" 
            size="small" 
            text 
            rounded 
            @click="visible = false"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
const isFullscreen = ref(false)

const dialogStyle = computed(() => {
  if (isFullscreen.value) {
    return { 
      width: '100vw', 
      height: '100vh', 
      maxWidth: 'none',
      margin: 0,
      top: 0,
      left: 0
    }
  }
  return { width: '95vw', height: '95vh', maxWidth: 'none' }
})

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}
</script>
```

### **NxFileManager.vue** Integration
```vue
<template>
  <!-- Sidebar Preview -->
  <NxFilePreviewPane
    :selectedFile="selectedFile"
    @open-fullscreen-dialog="showFullscreenView = true; fullscreenViewFile = selectedFile"
  />

  <!-- Fullscreen Dialog -->
  <NxFileViewDialog
    v-model:visible="showFullscreenView"
    :selectedFile="fullscreenViewFile"
  />
</template>
```

### **BEHAVIOR MATRIX**

| Context | Maximize Button Does | Close/Escape Does |
|---------|---------------------|-------------------|
| **Sidebar** | Opens fullscreen dialog | Closes sidebar |
| **Dialog (normal)** | Expands to full browser area | Closes dialog |
| **Dialog (fullscreen)** | Minimizes back to dialog size | Closes dialog |

### **KEY BENEFITS**

1. **Context-Aware**: Same `NxFileView` component behaves differently based on `maximizeMode`
2. **Space-Efficient**: Overlay buttons don't take extra UI space
3. **Consistent UX**: Maximize always expands, behavior depends on context
4. **Flexible**: Easy to add more maximize modes in the future
5. **Clean Architecture**: Single component handles all viewing logic

