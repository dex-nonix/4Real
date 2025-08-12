# 📝 DynamicForm Component

## 🎯 **PURPOSE:**
**Generic form builder that uses the widget manager system to render any form based on configuration**

## 🏗️ **ARCHITECTURE:**

### **Core Concept:**
- **Configuration-driven forms** - no hardcoded form layouts
- **Widget manager integration** - uses FormWidgetManager for field rendering
- **Generic value handling** - works with any PrimeVue input component
- **Reusable across all entities** - artists, albums, tracks, etc.

## 🔧 **IMPLEMENTATION:**

### **1. DynamicForm.vue Component:**
```vue
<template>
  <div class="dynamic-form">
    <form @submit.prevent="handleSubmit">
      <div v-for="(field, key) in config.fields" :key="key" class="form-field">
        <!-- Field Label -->
        <label :for="key" class="field-label">
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
      
      <!-- Form Actions -->
      <div class="form-actions">
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
import { FormWidgetManager } from '@/widgets/FormWidgetManager.js'
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
  max-width: 600px;
  margin: 0 auto;
}

.form-field {
  margin-bottom: 1.5rem;
}

.field-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.required {
  color: #ef4444;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}
</style>
```

## 📋 **CRUD CONFIG INTEGRATION:**

### **Artist Form Configuration:**
```javascript
// crud-configs/artist.js
export const artistCrudConfig = {
  entity: 'artist',
  form: {
    fields: {
      name: {
        type: 'text',                    // Maps to PrimeVue InputText
        label: 'Artist Name',
        required: true,
        props: {                         // PROPS PROPERTY!
          placeholder: 'Enter artist name',
          maxLength: 100
        }
      },
      abbreviation: {
        type: 'text',                    // Maps to PrimeVue InputText
        label: 'Abbreviation',
        required: true,
        props: {                         // PROPS PROPERTY!
          placeholder: 'Enter abbreviation',
          maxLength: 10
        }
      },
      persona: {
        type: 'rich_text',               // Maps to PrimeVue Editor
        label: 'Artist Persona',
        props: {                         // PROPS PROPERTY!
          height: '200px',
          toolbar: ['bold', 'italic', 'underline']
        }
      },
      albums: {
        type: 'multi_select',            // Maps to PrimeVue MultiSelect
        label: 'Albums',
        props: {                         // PROPS PROPERTY!
          options: [],                   // Will be populated from API
          placeholder: 'Choose albums',
          filter: true
        }
      },
      birth_date: {
        type: 'date',                    // Maps to PrimeVue Calendar
        label: 'Birth Date',
        props: {                         // PROPS PROPERTY!
          dateFormat: 'yy-mm-dd',
          showIcon: true
        }
      }
    }
  }
}
```

## 🔄 **VALUE HANDLING:**

### **PrimeVue Integration:**
- **`modelValue`** - Standard PrimeVue v-model binding
- **`@update:model-value`** - Generic value change handler
- **`value` prop** - For non-input components (display only)

### **Form Data Flow:**
1. **Initial data** passed via `initialData` prop
2. **Field changes** emit `field-change` event with new value
3. **Form submission** emits `submit` event with complete form data
4. **Validation** happens before submission

## 📁 **USAGE:**

### **In Artist Management View:**
```vue
<template>
  <div class="artist-form">
    <h2>{{ isEditing ? 'Edit Artist' : 'Create Artist' }}</h2>
    
    <DynamicForm
      :config="artistCrudConfig.form"
      :initial-data="artistData"
      :submit-label="isEditing ? 'Update Artist' : 'Create Artist'"
      @submit="handleSubmit"
      @cancel="$router.push('/artists')"
    />
  </div>
</template>

<script>
import DynamicForm from '@/components/core/DynamicForm.vue'
import { artistCrudConfig } from '@/configs/crud/artist.js'

export default {
  components: { DynamicForm },
  data() {
    return {
      artistCrudConfig,
      artistData: {},
      isEditing: false
    }
  },
  methods: {
    async handleSubmit(formData) {
      if (this.isEditing) {
        await this.updateArtist(formData)
      } else {
        await this.createArtist(formData)
      }
    }
  }
}
</script>
```

## 🎯 **KEY FEATURES:**

### **✅ Generic Form Building:**
- **Any entity type** - artists, albums, tracks, etc.
- **Dynamic field rendering** - based on widget manager
- **Flexible layouts** - vertical, horizontal, grid

### **✅ Widget Manager Integration:**
- **FormWidgetManager** - handles all form input widgets
- **Default props** - sensible defaults for each widget type
- **User props** - override defaults when needed

### **✅ PrimeVue Compatibility:**
- **All PrimeVue components** - InputText, Dropdown, MultiSelect, etc.
- **Standard v-model** - works with any PrimeVue input
- **Consistent styling** - PrimeVue design system

### **✅ Form Validation:**
- **Required field validation** - automatic error display
- **Custom validation** - extendable validation system
- **Error handling** - user-friendly error messages

**This gives you a completely generic form system that works with any entity and any widget type!** 