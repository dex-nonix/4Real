<template>
  <div class="dynamic-form" :class="formClasses">
    <form @submit.prevent="handleSubmit">
      <div class="form-fields" :class="fieldsLayout">
        <div
          v-for="(item, idx) in effectiveItems"
          :key="item.key ? item.key : `__ui_${idx}`"
          class="form-field"
        >
          <!-- Field Label (always render to preserve spacing) -->
          <label :for="item.key || `__ui_${idx}`" class="field-label" :class="labelClasses">
            {{ item.label || '' }}
            <span v-if="item.required" class="required">*</span>
          </label>

          <!-- Dynamic Widget Rendering -->
          <component 
            :is="resolveWidget(item.type).component"
            :id="item.key || `__ui_${idx}`"
            v-bind="{ ...resolveWidget(item.type).props, ...(item.props || {}) }"
            v-if="item.key"
            :model-value="formData[item.key]"
            @update:model-value="updateField(item.key, $event)"
            :class="{ 'error': item.key && fieldErrors[item.key] }"
          />
          <component
            v-else
            :is="resolveWidget(item.type).component"
            :id="`__ui_${idx}`"
            v-bind="{ ...resolveWidget(item.type).props, ...(item.props || {}) }"
          />

          <!-- Field Error Display -->
          <small v-if="item.key && fieldErrors[item.key]" class="error-message">
            {{ fieldErrors[item.key] }}
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
      return this.formManager.getWidget(type, {})
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
    
    // Build effective items from array-based config and check()
    computeEffectiveItems() {
      const fieldsArray = Array.isArray(this.config.fields) ? this.config.fields : []
      const result = []
      for (let index = 0; index < fieldsArray.length; index += 1) {
        const item = fieldsArray[index]
        const checkFn = typeof item.check === 'function' ? item.check : null
        if (!checkFn) {
          result.push(item)
          continue
        }
        const decision = checkFn(this.formData, index, item)
        if (decision === false) {
          continue
        }
        if (decision == null || decision === true) {
          result.push(item)
          continue
        }
        if (Array.isArray(decision)) {
          result.push(item, ...decision)
          continue
        }
        if (typeof decision === 'object') {
          result.push(decision)
          continue
        }
        // default fallback
        result.push(item)
      }
      return result
    },

    // Validate form (only visible items with keys)
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
    // Existing computed properties retained
    effectiveItems() {
      return this.computeEffectiveItems()
    }
  }
}
</script>

<style scoped>
.dynamic-form {
  width: 100%;
}

/* Base spacing to ensure sane defaults regardless of layout */
.form-fields {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label {
  margin-bottom: 0.5rem;
  font-weight: 500;
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
  gap: 0.5rem;
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
  gap: 0.5rem;
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
