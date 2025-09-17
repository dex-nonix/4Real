# File Manager Component Integration Guide

## Current Issues Analysis

### 1. Component Structure Issues

- **NxFileManager.vue**: 
  - Using Splitter layout that forces fullscreen-style display
  - Not designed to work as an inline component
  - Uses fixed height (`height: 100vh`) in CSS which prevents inline usage

- **NxFileTree.vue**:
  - Implemented as a sidebar panel instead of an inline component
  - Custom styling when PrimeFlex could be used
  - Already uses PrimeVue Tree component but with custom wrappers

- **NxFilePreviewPane.vue**:
  - Designed as separate pane rather than inline component
  - Custom CSS structure with `.file-preview-pane` instead of PrimeFlex
  - Good use of PrimeVue components internally

- **NxFilePreview.vue**:
  - Essential specialized component for file type rendering
  - Already uses PrimeIcons correctly
  - Minimal custom CSS (good)

- **NxFileListView.vue**:
  - Uses DataView component properly
  - Some custom CSS when PrimeFlex could be used

### 2. CSS Usage Issues

- Too many custom CSS classes instead of PrimeFlex utilities
- Examples of custom CSS that should be replaced:
  - `.file-preview-pane` → `flex flex-column h-full`
  - `.preview-header` → `flex justify-content-between align-items-center p-2 border-bottom-1 surface-border`
  - `.detail-row` → `flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border`

### 3. Layout Problems

- File tree forces sidebar layout rather than allowing inline usage
- Preview pane opens as a separate section instead of being inline with other content
- Components not designed to be flexible in different containers

## Integration Steps

### Step 1: Fix NxFileManager.vue

1. Remove fixed height styling:
```css
/* Replace this */
.file-manager {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* With PrimeFlex */
.file-manager {
  /* Remove height: 100vh */
  /* Use flex classes in template instead */
}
```

2. Make Splitter optional with prop:
```js
// Add new prop
const props = defineProps({
  // ...existing props
  useSplitter: { type: Boolean, default: true },
})
```

3. Add template option for inline layout:
```html
<!-- Add conditional wrapper -->
<template>
  <div class="file-manager" :class="{ 'mobile': isMobile }">
    <template v-if="useSplitter">
      <!-- Existing Splitter implementation -->
    </template>
    <template v-else>
      <!-- New inline implementation -->
      <div class="flex flex-column h-full">
        <!-- Simplified layout without fixed panes -->
      </div>
    </template>
  </div>
</template>
```

### Step 2: Fix NxFileTree.vue

1. Replace custom CSS with PrimeFlex:
```css
/* Replace custom styling */
.file-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Use PrimeFlex classes in template */
<div class="flex flex-column h-full">
```

2. Make height configurable:
```js
// Add new prop
const props = defineProps({
  // ...existing props
  treeHeight: { type: String, default: '100%' },
})
```

3. Add style binding:
```html
<div class="flex flex-column" :style="{ height: treeHeight }">
```

### Step 3: Fix NxFilePreviewPane.vue

1. Replace custom CSS with PrimeFlex:
```css
/* Replace */
.file-preview-pane {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--surface-border);
}

/* With classes in template */
<div class="flex flex-column h-full border-left-1 surface-border">
```

2. Add optional Card wrapper:
```js
// Add prop
const props = defineProps({
  // ...existing props
  useCard: { type: Boolean, default: false },
})
```

3. Add conditional Card component:
```html
<template>
  <Card v-if="useCard && selectedFile">
    <!-- Content -->
  </Card>
  <div v-else-if="selectedFile" class="flex flex-column h-full border-left-1 surface-border">
    <!-- Content -->
  </div>
  <!-- No selection state -->
</template>
```

### Step 4: Convert CSS to PrimeFlex

#### NxFileManager.vue
- `.file-manager-splitter` → `h-full border-1 surface-border`
- `.mobile-header` → `flex justify-content-between align-items-center p-2 border-bottom-1 surface-border bg-surface-section`
- `.mobile-content` → `flex-1 overflow-hidden`

#### NxFilePreviewPane.vue
- `.preview-header` → `flex justify-content-between align-items-center p-2 border-bottom-1 surface-border`
- `.preview-content` → `flex-1 p-3 overflow-y-auto`
- `.detail-row` → `flex justify-content-between mb-2 pb-1 border-bottom-1 surface-border`
- `.preview-actions` → `flex flex-wrap gap-2`

#### NxFileTree.vue
- `.tree-header` → `flex justify-content-between align-items-center p-2 border-bottom-1 surface-border`
- `.category-item` → `flex align-items-center p-2 cursor-pointer border-radius-2 transition-all transition-duration-200`
- `.category-item.selected` → `bg-primary-50 text-primary-700`

### Step 5: Add Integration Options

1. Create new exportable components:
   - `NxInlineFileManager.vue` - For embedding in other components
   - `NxFilePickerDialog.vue` - For selection dialogs

2. Add props to control appearance:
   - `compact: Boolean` - Use more compact styling
   - `height: String` - Control component height
   - `showTree: Boolean` - Show/hide tree
   - `showPreview: Boolean` - Show/hide preview

3. Create PrimeVue-friendly wrappers:
   - Dialog wrapper for file picker
   - Panel wrapper for inline display

## Implementation Notes

1. **DO NOT REMOVE specialized functionality**:
   - Keep NxFilePreview.vue as is - it handles multiple file types
   - Maintain file type detection and specialized renderers

2. **Preserve service integrations**:
   - fileTypeManager service for file type detection
   - fileOperationsService for file operations
   - categoryService for categories

3. **Component separation remains valid**:
   - NxFilePreview.vue - Core preview for file types
   - NxFilePreviewPane.vue - Detailed view with actions
   - NxFileListView.vue - List/grid view of files
   - NxFileTree.vue - Category navigation

4. **CSS conversion priorities**:
   - Replace custom flex layouts with PrimeFlex
   - Keep specialized styling where necessary
   - Don't compromise functionality for PrimeFlex purity

5. **Update all imports**:
   - Ensure all components import PrimeVue components
   - Add any missing PrimeFlex imports

## Testing Checklist

After implementation, verify:

- [ ] Components work inline without taking full screen
- [ ] File preview still handles all file types correctly
- [ ] Responsive behavior works on mobile devices
- [ ] PrimeFlex styling is consistent
- [ ] All file operations (upload, delete, etc.) still work
- [ ] Tree navigation and selection works correctly
