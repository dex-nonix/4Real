# 📝 DynamicForm Component

## 🎯 **PURPOSE:**
**Generic form builder that uses the widget manager system to render any form based on configuration - works for forms, filters, search, settings, etc.**

## 🏗️ **ARCHITECTURE:**

### **Core Concept:**
- **Configuration-driven forms** - no hardcoded form layouts
- **Widget manager integration** - uses FormWidgetManager for field rendering
- **Generic value handling** - works with any PrimeVue input component
- **Flexible layouts** - vertical (default), horizontal, compact for filters
- **Reusable across all entities** - artists, albums, tracks, etc.

### **FormWidgetManager Integration:**
The DynamicForm component uses the **FormWidgetManager** class to resolve and render form field widgets. The FormWidgetManager:

- **Extends BaseWidgetManager** - inherits generic widget management capabilities
- **Manages form-specific widgets** - text inputs, selects, multi-selects, etc.
- **Handles default props** - provides sensible defaults for each widget type
- **Allows prop overrides** - user props can override default widget behavior
- **Co-located with form component** - lives in the same `components/forms/` folder

#### **How FormWidgetManager Works:**
```javascript
// In DynamicForm.vue
data() {
  return {
    formManager: new FormWidgetManager(), // Creates form widget manager
    // ... other data
  }
},

methods: {
  // Resolve widget using FormWidgetManager
  resolveWidget(type) {
    return this.formManager.getWidget(type, {}, null) // Gets widget with default props
  }
}
```

The FormWidgetManager automatically resolves widget types like `'text'`, `'select'`, `'multi_select'` to their corresponding Vue components (TextInput, SelectInput, MultiSelect) and applies default styling and behavior.

### **Form Widget Registry (form-widgets.js):**
The FormWidgetManager uses a registry file that maps widget types to actual Vue components:

```javascript
// components/forms/form-widgets.js
import TextInput from '@/components/inputs/TextInput.vue'
import SelectInput from '@/components/inputs/SelectInput.vue'
import MultiSelect from '@/components/inputs/MultiSelect.vue'
import Autocomplete from '@/components/inputs/Autocomplete.vue'
import Slider from '@/components/inputs/Slider.vue'
import DateInput from '@/components/inputs/DateInput.vue'
import FileUpload from '@/components/inputs/FileUpload.vue'
import JsonEditor from '@/components/inputs/JsonEditor.vue'

export const FORM_WIDGETS = {
  'text': {
    component: TextInput,             // Actual Vue component import
    defaultProps: { 
      placeholder: 'Enter text',
      class: 'w-full'
    }
  },
  'select': {
    component: SelectInput,           // Actual Vue component import
    defaultProps: { 
      placeholder: 'Select option',
      class: 'w-full'
    }
  },
  'multi_select': {
    component: MultiSelect,           // Actual Vue component import
    defaultProps: { 
      placeholder: 'Select options',
      class: 'w-full'
    }
  },
  'autocomplete': {
    component: Autocomplete,          // Actual Vue component import
    defaultProps: { 
      placeholder: 'Type to search',
      minLength: 2,
      delay: 300
    }
  },
  'slider': {
    component: Slider,                // Actual Vue component import
    defaultProps: { 
      min: 0,
      max: 100,
      step: 1
    }
  },
  'date': {
    component: DateInput,             // Actual Vue component import
    defaultProps: { 
      dateFormat: 'yy-mm-dd',
      class: 'w-full'
    }
  },
  'file': {
    component: FileUpload,            // Actual Vue component import
    defaultProps: { 
      multiple: false,
      accept: '*'
    }
  },
  'json': {
    component: JsonEditor,            // Actual Vue component import
    defaultProps: { 
      height: '200px',
      readOnly: false
    }
  }
}
```

This registry file lives in the same `components/forms/` folder as the DynamicForm component and FormWidgetManager.

## 🔧 **IMPLEMENTATION:**

### **1. DynamicForm.vue Component:**
```vue
<template>
  <div class="dynamic-form" :class="formClasses">
    <form @submit.prevent="handleSubmit">
      <div class="form-fields" :class="fieldsLayout">
        <div v-for="(field, key) in config.fields" :key="key" class="form-field">
          <!-- Field Label -->
          <label :for="key" class="field-label" :class="labelClasses">
            {{ field.label }}
            <span v-if="field.required" class="required">*</span>
          </label>
          
          <!-- Dynamic Widget Rendering -->
          <component 
            :is="resolveWidget(field.type).component"
            :id="key"
            v-bind="resolveWidget(field.type).props"
            :model-value="formData[key]"
            @update:model-value="updateField(key, $event)"
            :class="{ 'error': fieldErrors[key] }"
          />
          
          <!-- Field Error Display -->
          <small v-if="fieldErrors[key]" class="error-message">
            {{ fieldErrors[key] }}
          </small>
        </div>
      </div>
      
      <!-- Form Actions (hidden for compact mode) -->
      <div v-if="!compact" class="form-actions">
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
import { FormWidgetManager } from './FormWidgetManager.js'
import { Button } from 'primevue/button'

export default {
  name: 'DynamicForm',
  components: { Button },
  
  props: {
    config: {
      type: Object,
      required: true
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
      formManager: new FormWidgetManager(),
      formData: { ...this.initialData },
      fieldErrors: {},
      isSubmitting: false
    }
  },
  
  methods: {
    // Resolve widget using FormWidgetManager
    resolveWidget(type) {
      return this.formManager.getWidget(type, {}, null)
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
    
    // Validate form
    validateForm() {
      this.fieldErrors = {}
      let isValid = true
      
      for (const [key, field] of Object.entries(this.config.fields)) {
        if (field.required && !this.formData[key]) {
          this.fieldErrors[key] = `${field.label} is required`
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
  }
}
</script>

<style scoped>
.dynamic-form {
  width: 100%;
}

/* Vertical Layout (default) */
.layout-vertical .form-fields {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.layout-vertical .form-field {
  display: flex;
  flex-direction: column;
}

.layout-vertical .field-label {
  margin-bottom: 0.5rem;
  font-weight: 500;
}

/* Horizontal Layout */
.layout-horizontal .form-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: end;
}

.layout-horizontal .form-field {
  display: flex;
  flex-direction: column;
  min-width: 200px;
}

.layout-horizontal .field-label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  white-space: nowrap;
}

/* Compact Mode */
.compact .form-fields {
  gap: 0.75rem;
}

.compact .form-field {
  margin-bottom: 0;
}

.compact .field-label {
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.compact .error-message {
  font-size: 0.75rem;
  margin-top: 0.125rem;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

/* Error Styling */
.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.required {
  color: #ef4444;
}
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

## 📋 **CONFIGURATION EXAMPLES:**

### **Artist Form (Vertical, Full):**
```javascript
// crud-configs/artist.js
export const artistFormConfig = {
  fields: {
    name: {
      type: 'text',
      label: 'Artist Name',
      required: true,
      props: { 
        placeholder: 'Enter artist name',
        class: 'w-full'
      }
    },
    abbreviation: {
      type: 'text',
      label: 'Abbreviation',
      required: true,
      props: { 
        placeholder: 'Enter abbreviation',
        class: 'w-full'
      }
    },
    persona: {
      type: 'rich_text',
      label: 'Artist Persona',
      props: { 
        height: '200px',
        toolbar: ['bold', 'italic', 'underline']
      }
    }
  }
}
```

### **Artist Filter (Horizontal, Compact):**
```javascript
// filter-configs/artist-filters.js
export const artistFilterConfig = {
  fields: {
    search: {
      type: 'text',
      label: 'Search',
      props: { 
        placeholder: 'Search artists...',
        class: 'w-64'
      }
    },
    status: {
      type: 'select',
      label: 'Status',
      props: { 
        options: ['active', 'inactive'],
        placeholder: 'All statuses',
        class: 'w-32'
      }
    },
    dateRange: {
      type: 'date_range',
      label: 'Date Range',
      props: { 
        class: 'w-48'
      }
    }
  }
}
```

### **Search Form (Horizontal, Compact):**
```javascript
// search-configs/global-search.js
export const globalSearchConfig = {
  fields: {
    query: {
      type: 'text',
      label: 'Search',
      props: { 
        placeholder: 'Search everything...',
        class: 'w-80'
      }
    },
    entity: {
      type: 'select',
      label: 'Entity',
      props: { 
        options: ['all', 'artists', 'albums', 'tracks'],
        class: 'w-32'
      }
    }
  }
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
- **`layout="horizontal"`** - side-by-side fields
- **`:compact="true"`** - tight spacing
- **No over-engineering** - just layout props

### **✅ Widget Manager Integration:**
- **Same input widgets** - work in any layout
- **Consistent behavior** - same validation, same events
- **Reusable system** - one component, many use cases

**This gives you ONE form component that handles ALL form scenarios - just change the layout props!** 