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
import FormWidgetManager from '@/components/forms/FormWidgetManager.js'
import Button from 'primevue/button'

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
