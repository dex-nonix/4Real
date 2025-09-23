# **PHASE-BY-PHASE IMPLEMENTATION PLAN: Context-Aware Maximize in NxFileView**

## **OVERVIEW**
Implement context-aware maximize functionality where the same `NxFileView` component behaves differently based on context:
- **Sidebar context**: Maximize opens fullscreen dialog
- **Dialog context**: Maximize toggles true fullscreen browser mode

---

## **PHASE 1: ANALYSIS & PLANNING**

### **Step 1.1: Analyze Current NxFilePreviewPane.vue**
- **Task**: Document all current functionality in NxFilePreviewPane.vue
- **Details**:
  - File preview rendering (image, audio, video, icons)
  - File details display (name, size, type, category, created date, dimensions, duration)
  - Action buttons (download, rename, copy, move, delete)
  - Rename dialog functionality
  - Mobile vs desktop layouts
  - Card vs non-card display modes
  - Styling and responsive behavior
- **Output**: Complete feature inventory for migration

### **Step 1.2: Define NxFileView Component API**
- **Task**: Design props, emits, and behavior matrix
- **Props**:
  - `selectedFile: Object` (required)
  - `maximizeMode: String` (default: 'dialog', values: 'dialog'|'fullscreen')
- **Emits**:
  - `open-fullscreen-dialog` (when maximizeMode='dialog')
- **Behavior Matrix**:
  - Sidebar + Maximize → Opens NxFileViewDialog
  - Dialog + Maximize → Toggles fullscreen
  - Dialog + Minimize → Returns to normal dialog size

### **Step 1.3: Define NxFileViewDialog Component API**
- **Task**: Design dialog wrapper with custom controls
- **Props**:
  - `visible: Boolean`
  - `selectedFile: Object`
- **Features**:
  - Custom header with maximize/minimize/close buttons
  - Dynamic styling based on fullscreen state
  - Proper modal behavior and sizing

---

## **PHASE 2: CORE COMPONENTS CREATION**

### **Step 2.1: Create NxFileView.vue Component**
- **Task**: Build the core file viewing component
- **Template Structure**:
  ```vue
  <div class="file-view" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- Image Preview with Overlay Maximize Button -->
    <div v-if="isImage && previewUrl" class="image-preview-container">
      <img :src="previewUrl" :style="imageStyle" />
      <Button icon="pi pi-expand" class="maximize-overlay-btn" ... />
    </div>

    <!-- Audio Preview -->
    <div v-else-if="isAudio && previewUrl" class="audio-preview">
      <audio :src="previewUrl" controls :style="mediaStyle"></audio>
    </div>

    <!-- Video Preview with Overlay -->
    <div v-else-if="isVideo && previewUrl" class="video-preview-container">
      <video :src="previewUrl" controls :style="mediaStyle"></video>
      <Button icon="pi pi-expand" class="maximize-overlay-btn" ... />
    </div>

    <!-- File Icon for other types -->
    <div v-else class="file-icon-preview">
      <NxFilePreview :value="selectedFile" :style="iconStyle" />
    </div>

    <!-- File Details & Actions (migrated from NxFilePreviewPane) -->
  </div>
  ```

- **Script Logic**:
  - Import all necessary PrimeVue components (Button, Dialog, etc.)
  - Implement maximizeMode prop validation
  - Add computed properties for dynamic styling
  - Implement handleMaximize method with context-aware behavior
  - Migrate all preview logic from NxFilePreviewPane

- **Styling**:
  - Use PrimeFlex classes only (no custom CSS)
  - Position overlay buttons absolutely
  - Define fullscreen vs normal mode styles

### **Step 2.2: Create NxFileViewDialog.vue Component**
- **Task**: Build the dialog wrapper component
- **Template Structure**:
  ```vue
  <Dialog
    v-model:visible="visible"
    modal
    :header="selectedFile?.title || selectedFile?.original_filename"
    :style="dialogStyle"
    :closable="false"  <!-- We handle close ourselves -->
  >
    <!-- Custom Header Template -->
    <template #header>
      <div class="flex justify-content-between align-items-center w-full">
        <span>{{ selectedFile.title || selectedFile.original_filename }}</span>
        <div class="flex gap-2">
          <Button :icon="isFullscreen ? 'pi pi-minus' : 'pi pi-expand'"
                  size="small" text rounded
                  v-tooltip="isFullscreen ? 'Minimize' : 'Maximize'"
                  @click="toggleFullscreen" />
          <Button icon="pi pi-times" size="small" text rounded
                  @click="visible = false" />
        </div>
      </div>
    </template>

    <!-- NxFileView with fullscreen maximizeMode -->
    <NxFileView :selectedFile="selectedFile" :maximizeMode="'fullscreen'" />
  </Dialog>
  ```

- **Script Logic**:
  - Import PrimeVue Dialog and Button
  - Add isFullscreen ref for toggle state
  - Implement dialogStyle computed for dynamic sizing
  - Add toggleFullscreen method

### **Step 2.3: Migrate File Details & Actions**
- **Task**: Move file details and action buttons from NxFilePreviewPane to NxFileView
- **Details**:
  - File metadata display (name, size, type, category, created date)
  - Image dimensions and video duration display
  - Action buttons (download, rename, copy, move, delete)
  - Rename dialog functionality
  - All associated computed properties and methods

---

## **PHASE 3: INTEGRATION & STATE MANAGEMENT**

### **Step 3.1: Update NxFileManager.vue State**
- **Task**: Add fullscreen dialog state management
- **Changes**:
  - Add `showFullscreenView: ref(false)`
  - Add `fullscreenViewFile: ref(null)`
  - Add method to open fullscreen dialog:
    ```javascript
    const openFullscreenView = (file) => {
      fullscreenViewFile.value = file
      showFullscreenView.value = true
    }
    ```

### **Step 3.2: Integrate NxFileViewDialog in NxFileManager.vue**
- **Task**: Add the fullscreen dialog to the template
- **Location**: After existing dialogs (bulk operations, mobile preview)
- **Template Addition**:
  ```vue
  <!-- Fullscreen File View Dialog -->
  <NxFileViewDialog
    v-model:visible="showFullscreenView"
    :selectedFile="fullscreenViewFile"
  />
  ```

### **Step 3.3: Update NxFilePreviewPane.vue**
- **Task**: Replace internal preview logic with NxFileView component
- **Changes**:
  - Import NxFileView component
  - Replace preview rendering with:
    ```vue
    <NxFileView
      :selectedFile="selectedFile"
      :maximizeMode="'dialog'"
      @open-fullscreen-dialog="$emit('open-fullscreen-dialog')"
    />
    ```
  - Remove duplicate file details and actions (now in NxFileView)
  - Keep only the wrapper Card/layout logic

### **Step 3.4: Update NxFileManager.vue Preview Pane Usage**
- **Task**: Connect NxFilePreviewPane to fullscreen dialog
- **Changes**:
  ```vue
  <NxFilePreviewPane
    :selectedFile="selectedFile"
    @close="selectedFile = null"
    @file-action="handleFileAction"
    @file-renamed="handleFileRenamed"
    @open-fullscreen-dialog="openFullscreenView(selectedFile)"
  />
  ```

---

## **PHASE 4: STYLING & RESPONSIVE DESIGN**

### **Step 4.1: Implement Overlay Button Styling**
- **Task**: Style maximize overlay buttons using PrimeFlex
- **Requirements**:
  - Absolute positioning over image/video previews
  - Top-right corner placement
  - Semi-transparent background with hover effect
  - Proper z-index for overlay

### **Step 4.2: Dynamic Sizing Logic**
- **Task**: Implement computed styles for different modes
- **Image Styles**:
  - Normal: `maxHeight: '200px'`
  - Fullscreen: `maxHeight: '80vh'`
- **Media Styles**:
  - Normal: `maxHeight: '200px'`
  - Fullscreen: `maxHeight: '70vh'`
- **Icon Styles**:
  - Normal: `fontSize: '3rem'`
  - Fullscreen: `fontSize: '5rem'`

### **Step 4.3: Dialog Fullscreen Styling**
- **Task**: Dynamic dialog dimensions for fullscreen mode
- **Normal Dialog**: `width: '95vw', height: '95vh'`
- **Fullscreen Dialog**: `width: '100vw', height: '100vh', margin: 0, top: 0, left: 0`

---

## **PHASE 5: TESTING & VERIFICATION**

### **Step 5.1: PrimeVue Compliance Audit**
- **Task**: Verify all components follow PrimeVue-first rule
- **Checklist**:
  - ✅ All buttons use `<Button>` component
  - ✅ All dialogs use `<Dialog>` component
  - ✅ All layouts use PrimeFlex classes
  - ✅ All icons use PrimeIcons (`pi pi-*`)
  - ✅ No custom CSS for layout/flexbox
  - ✅ No custom button/modal components

### **Step 5.2: Context-Aware Behavior Testing**
- **Task**: Test maximize functionality in different contexts
- **Test Cases**:
  1. **Sidebar Context**:
     - Select file → Preview shows in sidebar
     - Click maximize button → Opens fullscreen dialog
     - Dialog maximize button → Expands to browser fullscreen
     - Dialog minimize button → Returns to normal dialog
     - Close button → Closes dialog, returns to sidebar

  2. **Mobile Context**:
     - Select file → Opens mobile preview modal
     - Maximize button → Opens fullscreen dialog
     - Test fullscreen toggle in mobile browser

  3. **Direct Dialog Usage**:
     - Open file directly in dialog
     - Maximize toggles fullscreen mode
     - Minimize returns to dialog size

### **Step 5.3: Responsive Testing**
- **Task**: Verify behavior across screen sizes
- **Breakpoints**:
  - Desktop (>768px): Splitter layout with sidebar
  - Mobile (≤768px): Modal-based preview
  - Test overlay button positioning
  - Test dialog sizing in fullscreen

### **Step 5.4: File Type Testing**
- **Task**: Verify maximize works for all file types
- **File Types**:
  - Images: Overlay maximize button, proper scaling
  - Videos: Overlay maximize button, proper scaling
  - Audio: No overlay button (audio doesn't benefit from maximize)
  - Documents/PDFs: Icon preview with larger icon in fullscreen

---

## **PHASE 6: CLEANUP & OPTIMIZATION**

### **Step 6.1: Remove Redundant Code**
- **Task**: Clean up NxFilePreviewPane.vue after migration
- **Remove**:
  - Duplicate preview rendering logic (now in NxFileView)
  - Duplicate file details display (now in NxFileView)
  - Duplicate action buttons (now in NxFileView)
  - Keep only wrapper Card and basic layout

### **Step 6.2: Update Imports and Dependencies**
- **Task**: Ensure all new components have proper imports
- **NxFileView.vue**: Import Button, NxFilePreview, utils
- **NxFileViewDialog.vue**: Import Dialog, Button, NxFileView
- **NxFileManager.vue**: Import NxFileViewDialog
- **NxFilePreviewPane.vue**: Import NxFileView

### **Step 6.3: Performance Optimization**
- **Task**: Optimize component rendering and state management
- **Considerations**:
  - Lazy loading of preview URLs
  - Efficient computed property caching
  - Minimal re-renders on maximize state changes

---

## **SUCCESS CRITERIA**

### **Functional Requirements**:
- ✅ Maximize button appears as overlay on images/videos
- ✅ Sidebar maximize opens fullscreen dialog
- ✅ Dialog maximize toggles true fullscreen
- ✅ All file types display correctly in both modes
- ✅ File details and actions work in all contexts

### **Technical Requirements**:
- ✅ PrimeVue-first compliance (no custom components when PrimeVue exists)
- ✅ PrimeFlex-only styling (no custom CSS for layout)
- ✅ PrimeIcons-only (no other icon libraries)
- ✅ Responsive design works on all screen sizes
- ✅ Context-aware behavior works correctly

### **User Experience Requirements**:
- ✅ Intuitive maximize/minimize controls
- ✅ Consistent behavior across different contexts
- ✅ Proper visual feedback for different states
- ✅ Smooth transitions between modes
- ✅ Accessible keyboard navigation

---

## **ROLLBACK PLAN**
If issues arise during implementation:

1. **Component-Level Rollback**: Comment out new NxFileView usage, revert to original NxFilePreviewPane
2. **File-Level Rollback**: Restore NxFilePreviewPane.vue from git if corrupted
3. **State-Level Rollback**: Remove fullscreen dialog state, restore simple preview modal

---

## **IMPLEMENTATION ORDER**
1. Create NxFileView.vue (core component)
2. Create NxFileViewDialog.vue (dialog wrapper)
3. Update NxFileManager.vue (add state and dialog)
4. Update NxFilePreviewPane.vue (integrate NxFileView)
5. Test and verify all functionality
6. Clean up and optimize
