# 📝 DynamicForm Component

## 🎯 **PURPOSE:**
**Generic form builder that uses the widget manager system to render any form based on configuration - works for forms, filters, search, settings, etc.**

## 🏗️ **ARCHITECTURE:**

### **Core Concept:**
- **Configuration-driven forms** - no hardcoded form layouts
- **Widget manager integration** - uses EditWidgetManager (edit) and DisplayWidgetManager (display)
- **Generic value handling** - works with any PrimeVue input component
- **Flexible layouts** - vertical (default), horizontal, compact for filters
- **Reusable across all entities** - artists, albums, tracks, etc.

### **Widget Manager Integration (edit/display):**
DynamicForm uses two managers to resolve widgets:
— EditWidgetManager for input (edit) widgets
— DisplayWidgetManager for read-only (display) widgets

- Both extend BaseWidgetManager, provide sensible defaults, and allow prop overrides

#### **How widget resolution works:**
```javascript
// In DynamicForm.vue
data() {
  return {
    editManager: new EditWidgetManager(),
    displayManager: new DisplayWidgetManager(),
    // ... other data
  }
},

methods: {
  // Resolve edit widget (string maps to registry; component passes through)
  resolveEditWidget(widget) {
    return typeof widget === 'string' 
      ? this.editManager.getWidget(widget, {}) 
      : { component: widget, props: {} }
  },
  // Resolve display widget (string maps to registry; component passes through)
  resolveDisplayWidget(widget) {
    return typeof widget === 'string' 
      ? this.displayManager.getWidget(widget, {}) 
      : { component: widget, props: {} }
  }
}
```

The FormWidgetManager automatically resolves widget types like `'text'`, `'select'`, `'multi_select'` to their corresponding Vue components (TextInput, SelectInput, MultiSelect) and applies default styling and behavior.

### **Edit Widget Registry (edit-widgets.js):**
The EditWidgetManager uses a registry file that maps widget types to actual Vue components:

```javascript
// widgets/edit-widgets.js (PrimeVue components)
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import AutoComplete from 'primevue/autocomplete'
import Slider from 'primevue/slider'
import Calendar from 'primevue/calendar'
import FileUpload from 'primevue/fileupload'
import Editor from 'primevue/editor'

export const EDIT_WIDGETS = {
  'text': { component: InputText, defaultProps: { placeholder: 'Enter text', class: 'w-full' } },
  'select': { component: Dropdown, defaultProps: { placeholder: 'Select option', class: 'w-full' } },
  'multi_select': { component: MultiSelect, defaultProps: { placeholder: 'Select options', class: 'w-full' } },
  'autocomplete': { component: AutoComplete, defaultProps: { placeholder: 'Type to search', minLength: 2, delay: 300 } },
  'slider': { component: Slider, defaultProps: { min: 0, max: 100, step: 1 } },
  'date': { component: Calendar, defaultProps: { dateFormat: 'yy-mm-dd', class: 'w-full' } },
  'file': { component: FileUpload, defaultProps: { multiple: false, accept: '*' } },
  'json': { component: Editor, defaultProps: { height: '200px', readOnly: false } }
}
```

Supported field types include: text, number, date, select, textarea, and json (for `*_json` fields like `metadata_json`, `config_json`).

Registries live under `widgets/`. Because we use PrimeVue components directly, no custom wrappers are required for standard fields.

## 🔧 **IMPLEMENTATION:**

### ⚠️ Field items (edit/display schema)

- `config.fields` is now an array of field items, rendered in order
- Each item uses a `key` to bind to `formData[key]`; items without `key` are allowed (UI-only/dataless)
- Each item may optionally define a `check(formData, index, item)` function that controls visibility and inline expansion

Field item shape:

```ts
type FieldItem = {
  key?: string
  label?: string
  required?: boolean
  check?: (formData: Record<string, any>, index: number, item: FieldItem) => boolean | null | FieldItem | FieldItem[]

  // Edit (input) widget
  editWidget: string | Component
  editProps?: Record<string, any>

  // Display (value) widget
  displayOnly?: boolean
  displayWidget?: string | Component // optional override; defaults to editWidget name
  displayProps?: Record<string, any>
}
```

Notes:
- Validation only applies to currently visible items that have a `key` and `required: true`.
- Hidden values are preserved (no clearing) to keep behavior minimal.
- Inline expansion: when `check` returns an array, those items are inserted immediately after the provider item for that render pass.

### **1. DynamicForm.vue Component (edit/display modes):**
```vue
<template>
  <div class="dynamic-form p-fluid" :class="formClasses">
    <form @submit.prevent="handleSubmit">
      <div class="form-fields formgrid grid gap-3" :class="fieldsLayout">
        <div
          v-for="(item, idx) in effectiveItems"
          :key="item.key ? item.key : `__ui_${idx}`"
          class="form-field field col-12"
        >
          <!-- Field Label (shown for items that declare a label) -->
          <label v-if="item.label" :for="item.key" class="field-label" :class="labelClasses">
            {{ item.label }}
            <span v-if="item.required" class="required">*</span>
          </label>

          <!-- Dynamic Widget Rendering (edit vs display) -->
          <component 
            v-if="(mode !== 'display') && !item.displayOnly"
            :is="resolveEditWidget(item.editWidget).component"
            :id="item.key || `__ui_${idx}`"
            v-bind="{ ...resolveEditWidget(item.editWidget).props, ...(item.editProps || {}) }"
            v-if="item.key"
            :model-value="formData[item.key]"
            @update:model-value="updateField(item.key, $event)"
            :class="{ 'error': item.key && fieldErrors[item.key] }"
          />
          <component
            v-else
            :is="resolveDisplayWidget(item.displayWidget || item.editWidget).component"
            :id="item.key || `__ui_${idx}`"
            v-bind="{ ...resolveDisplayWidget(item.displayWidget || item.editWidget).props, ...(item.displayProps || item.editProps || {}) }"
          />

          <!-- Field Error Display -->
          <small v-if="item.key && fieldErrors[item.key]" class="p-error">
            {{ fieldErrors[item.key] }}
          </small>
        </div>
      </div>
      
      <!-- Form Actions (hidden for compact mode) -->
      <div v-if="!compact" class="flex gap-3 justify-content-end mt-4">
        <Button type="submit" :loading="isSubmitting">
          {{ submitLabel }}
        </Button>
        <Button type="button" severity="secondary" @click="$emit('cancel')">
          Cancel
        </Button>
      </div>
    </form>
  </div>
</template>

<script>
import EditWidgetManager from '@/widgets/EditWidgetManager.js'
import DisplayWidgetManager from '@/widgets/DisplayWidgetManager.js'
import Button from 'primevue/button'

export default {
  name: 'DynamicForm',
  components: { Button },
  
  props: {
    config: {
      type: Object,
      required: true
    },
    mode: { // 'edit' | 'display'
      type: String,
      default: 'edit'
    },
    initialData: {
      type: Object,
      default: () => ({})
    },
    submitLabel: {
      type: String,
      default: 'Save'
    },
    layout: {
      type: String,
      default: 'vertical',
      validator: value => ['vertical', 'horizontal'].includes(value)
    },
    compact: {
      type: Boolean,
      default: false
    }
  },
  
  computed: {
    formClasses() {
      return {
        'compact': this.compact,
        [`layout-${this.layout}`]: true
      }
    },
    
    fieldsLayout() {
      return {
        'fields-vertical': this.layout === 'vertical',
        'fields-horizontal': this.layout === 'horizontal'
      }
    },
    
    labelClasses() {
      return {
        'label-compact': this.compact,
        'label-horizontal': this.layout === 'horizontal'
      }
    }
  },
  
  data() {
    return {
      editManager: new EditWidgetManager(),
      displayManager: new DisplayWidgetManager(),
      formData: { ...this.initialData },
      fieldErrors: {},
      isSubmitting: false
    }
  },
  
  methods: {
    // Resolve widgets using managers
    resolveEditWidget(widget) {
      return typeof widget === 'string' ? this.editManager.getWidget(widget, {}) : { component: widget, props: {} }
    },
    resolveDisplayWidget(widget) {
      return typeof widget === 'string' ? this.displayManager.getWidget(widget, {}) : { component: widget, props: {} }
    },
    
    // Update field value
    updateField(key, value) {
      this.formData[key] = value
      this.clearFieldError(key)
      this.$emit('field-change', { key, value, formData: this.formData })
    },
    
    // Clear field error
    clearFieldError(key) {
      if (this.fieldErrors[key]) {
        delete this.fieldErrors[key]
      }
    },
    
    // Compute visible/effective items based on `fields` array and `check`
    computeEffectiveItems() {
      const input = Array.isArray(this.config.fields) ? this.config.fields : []
      const output = []
      for (let i = 0; i < input.length; i += 1) {
        const item = input[i]
        const fn = typeof item.check === 'function' ? item.check : null
        if (!fn) {
          output.push(item)
          continue
        }
        const res = fn(this.formData, i, item)
        if (res === false) {
          continue
        }
        if (res == null || res === true) {
          output.push(item)
          continue
        }
        if (Array.isArray(res)) {
          output.push(item, ...res)
          continue
        }
        if (typeof res === 'object') {
          output.push(res)
          continue
        }
        // Fallback: show as-is
        output.push(item)
      }
      return output
    },

    // Validate form (only visible items with `key`)
    validateForm() {
      this.fieldErrors = {}
      let isValid = true
      const items = this.computeEffectiveItems()
      for (const item of items) {
        if (!item || !item.key) continue
        if (item.required && !this.formData[item.key]) {
          this.fieldErrors[item.key] = `${item.label || item.key} is required`
          isValid = false
        }
      }
      
      return isValid
    },
    
    // Handle form submission
    async handleSubmit() {
      if (!this.validateForm()) {
        return
      }
      
      this.isSubmitting = true
      
      try {
        await this.$emit('submit', this.formData)
      } catch (error) {
        console.error('Form submission error:', error)
      } finally {
        this.isSubmitting = false
      }
    }
  },
  
  // Watch for initial data changes
  watch: {
    initialData: {
      handler(newData) {
        this.formData = { ...newData }
      },
      deep: true
    }
  },

  computed: {
    // Existing computed props retained above
    effectiveItems() {
      return this.computeEffectiveItems()
    }
  }
}
</script>

<style scoped>
/* Use PrimeFlex utilities and PrimeVue theme; avoid custom CSS. */
</style>

## 📋 **LAYOUT CONFIGURATION:**

### **1. Vertical Layout (Default - for CRUD forms):**
```vue
<DynamicForm
  :config="artistFormConfig"
  layout="vertical"
  :compact="false"
  @submit="handleSubmit"
/>
```

### **2. Horizontal Layout (for filters, search):**
```vue
<DynamicForm
  :config="filterConfig"
  layout="horizontal"
  :compact="true"
  @field-change="handleFilterChange"
/>
```

### **3. Compact Mode (for inline forms, filters):**
```vue
<DynamicForm
  :config="searchConfig"
  layout="horizontal"
  :compact="true"
  @field-change="handleSearch"
/>
```

## 📋 **CONFIGURATION EXAMPLES (Array-based fields):**

### **Artist Form (Vertical, Full):**
```javascript
// crud-configs/artist.js
export const artistFormConfig = {
  fields: [
    {
      key: 'name',
      type: 'text',
      label: 'Artist Name',
      required: true,
      props: { placeholder: 'Enter artist name', class: 'w-full' }
    },
    {
      key: 'abbreviation',
      type: 'text',
      label: 'Abbreviation',
      required: true,
      props: { placeholder: 'Enter abbreviation', class: 'w-full' }
    },
    {
      key: 'status',
      type: 'select',
      label: 'Status',
      props: {
        options: [
          { label: 'Active', value: 'active' },
          { label: 'Inactive', value: 'inactive' },
          { label: 'Pending', value: 'pending' }
        ],
        class: 'w-full'
      },
      // Inline grow/shrink: add advanced fields when status is 'active'
      check: (formData) => {
        if (formData.status === 'active') {
          return [
            { key: 'advancedOption', type: 'text', label: 'Advanced Option' },
            { key: 'tuning', type: 'slider', label: 'Tuning' }
          ]
        }
        return true
      }
    },
    {
      key: 'persona',
      type: 'json',
      label: 'Artist Persona',
      props: { height: '200px', class: 'w-full' }
    },
    {
      // dataless UI-only item (no key)
      type: 'text',
      label: 'Note: Advanced fields appear when status is Active',
      check: (formData, i, item) => (formData.status === 'active' ? item : null)
    }
  ]
}
```

### **Artist Filter (Horizontal, Compact):**
```javascript
// filter-configs/artist-filters.js
export const artistFilterConfig = {
  fields: [
    {
      key: 'search',
      type: 'text',
      label: 'Search',
      props: { placeholder: 'Search artists...', class: 'w-12rem' }
    },
    {
      key: 'status',
      type: 'select',
      label: 'Status',
      props: {
        options: [
          { label: 'All', value: '' },
          { label: 'Active', value: 'active' },
          { label: 'Inactive', value: 'inactive' }
        ],
        class: 'w-8rem'
      }
    },
    {
      key: 'dateRange',
      type: 'date',
      label: 'Date Range',
      props: { class: 'w-48' }
    }
  ]
}
```

### **Search Form (Horizontal, Compact):**
```javascript
// search-configs/global-search.js
export const globalSearchConfig = {
  fields: [
    {
      key: 'query',
      type: 'text',
      label: 'Search',
      props: { placeholder: 'Search everything...', class: 'w-20rem' }
    },
    {
      key: 'entity',
      type: 'select',
      label: 'Entity',
      props: {
        options: [
          { label: 'All', value: 'all' },
          { label: 'Artists', value: 'artists' },
          { label: 'Albums', value: 'albums' },
          { label: 'Tracks', value: 'tracks' }
        ],
        class: 'w-8rem'
      }
    }
  ]
}
```

## 📁 **USAGE EXAMPLES:**

### **1. CRUD Form (Vertical, Full):**
```vue
<template>
  <div class="artist-form">
    <h2>{{ isEditing ? 'Edit Artist' : 'Create Artist' }}</h2>
    
    <DynamicForm
      :config="artistFormConfig"
      layout="vertical"
      :compact="false"
      :initial-data="artistData"
      :submit-label="isEditing ? 'Update Artist' : 'Create Artist'"
      @submit="handleSubmit"
      @cancel="$router.push('/artists')"
    />
  </div>
</template>
```

### **2. Filter Form (Horizontal, Compact):**
```vue
<template>
  <div class="artists-view">
    <!-- Filter Form -->
    <DynamicForm
      :config="artistFilterConfig"
      layout="horizontal"
      :compact="true"
      @field-change="handleFilterChange"
    />
    
    <!-- Data Table -->
    <DynamicTable :config="artistTableConfig" :data="filteredArtists" />
  </div>
</template>
```

### **3. Search Form (Horizontal, Compact):**
```vue
<template>
  <div class="search-bar">
    <DynamicForm
      :config="globalSearchConfig"
      layout="horizontal"
      :compact="true"
      @field-change="handleSearch"
    />
  </div>
</template>
```

## 🎯 **KEY FEATURES:**

### **✅ Flexible Layouts:**
- **Vertical layout** - traditional form layout (default)
- **Horizontal layout** - side-by-side fields for filters/search
- **Compact mode** - tight spacing for inline forms

### **✅ Universal Usage:**
- **CRUD forms** - vertical, full layout with buttons
- **Filter forms** - horizontal, compact, no buttons
- **Search forms** - horizontal, compact, no buttons
- **Settings forms** - vertical, full layout

### **✅ Simple Configuration:**
- **Array-based fields** with explicit order and optional `key` for binding
- **Minimal conditional logic** with `check(formData, index, item)` returning: false | true/null | object | array
- **`layout="horizontal"`** - side-by-side fields
- **`:compact="true"`** - tight spacing

### **✅ Widget Manager Integration:**
- **Same input widgets** - work in any layout
- **Consistent behavior** - same validation, same events
- **Reusable system** - one component, many use cases

**This gives you ONE form component that handles ALL form scenarios - just change the layout props!** 