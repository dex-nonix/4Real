<template>
  <div class="dynamic-form p-fluid" :class="formClasses">
    <form @submit.prevent="handleSubmit">
      <div class="form-fields formgrid grid gap-3" :class="fieldsLayout">
        <div
          v-for="(item, idx) in effectiveItems"
          :key="item.key ? item.key : `__ui_${idx}`"
          class="form-field field col-12"
        >
          <!-- Field Label (always render to preserve spacing) -->
          <label :for="item.key || `__ui_${idx}`" class="field-label" :class="labelClasses">
            {{ item.label || '' }}
            <span v-if="item.required" class="required">*</span>
          </label>

          <!-- Dynamic Widget Rendering (edit vs display) -->
          <template v-if="(mode !== 'display') && !item.displayOnly">
            <component 
              v-if="item.key"
              :is="resolveEditWidget(item.editWidget ?? item.type).component"
              :id="item.key || `__ui_${idx}`"
              v-bind="{ ...resolveEditWidget(item.editWidget ?? item.type).props, ...(item.editProps ?? item.props ?? {}) }"
              :model-value="formData[item.key]"
              @update:model-value="updateField(item.key, $event)"
              :class="{ 'error': item.key && fieldErrors[item.key] }"
            />
            <component
              v-else
              :is="resolveEditWidget(item.editWidget ?? item.type).component"
              :id="`__ui_${idx}`"
              v-bind="{ ...resolveEditWidget(item.editWidget ?? item.type).props, ...(item.editProps ?? item.props ?? {}) }"
            />
          </template>
          <component
            v-else
            :is="resolveDisplayWidget((item.displayWidget ?? item.editWidget ?? item.type)).component"
            :id="item.key || `__ui_${idx}`"
            v-bind="{ ...resolveDisplayWidget((item.displayWidget ?? item.editWidget ?? item.type)).props, ...(item.displayProps ?? item.editProps ?? item.props ?? {}) }"
          >
            {{ item.key ? formatDisplay(formData[item.key]) : '' }}
          </component>

          <!-- Field Error Display -->
          <small v-if="item.key && fieldErrors[item.key]" class="p-error">
            {{ fieldErrors[item.key] }}
          </small>
        </div>
      </div>
      
      <!-- Form Actions (hidden for compact mode and display mode) -->
      <div v-if="!compact && mode !== 'display'" class="flex gap-3 justify-content-end mt-4">
        <Button type="submit" :loading="isSubmitting" :disabled="isSubmitting">
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
import EditWidgetManager from '@nonix/widget-manager/EditWidgetManager.js'
import DisplayWidgetManager from '@nonix/widget-manager/DisplayWidgetManager.js'
import Button from 'primevue/button'

export default {
  name: 'DynamicForm',
  components: { Button },
  
  props: {
    config: {
      type: Object,
      required: true
    },
    mode: {
      type: String,
      default: 'edit' // 'edit' | 'display'
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
      changedValues: {},
      isDirty: false,
      fieldErrors: {},
      isSubmitting: false
    }
  },
  
  methods: {
    // Resolve widgets
    resolveEditWidget(widget) {
      return typeof widget === 'string' ? this.editManager.getWidget(widget, {}) : { component: widget, props: {} }
    },
    resolveDisplayWidget(widget) {
      return typeof widget === 'string' ? this.displayManager.getWidget(widget, {}) : { component: widget, props: {} }
    },
    formatDisplay(value) {
      return value == null ? '' : String(value)
    },
    deepEqual(a, b) {
      if (a === b) return true
      if (a == null || b == null) return a == null && b == null
      if (typeof a !== typeof b) return false
      if (Array.isArray(a) && Array.isArray(b)) {
        if (a.length !== b.length) return false
        for (let i = 0; i < a.length; i += 1) {
          if (!this.deepEqual(a[i], b[i])) return false
        }
        return true
      }
      if (typeof a === 'object' && typeof b === 'object') {
        const aKeys = Object.keys(a)
        const bKeys = Object.keys(b)
        if (aKeys.length !== bKeys.length) return false
        for (const k of aKeys) {
          if (!this.deepEqual(a[k], b[k])) return false
        }
        return true
      }
      return false
    },
    
    // Update field value
    updateField(key, value) {
      this.formData[key] = value
      this.clearFieldError(key)
      const original = this.initialData ? this.initialData[key] : undefined
      if (this.deepEqual(original, value)) {
        if (Object.prototype.hasOwnProperty.call(this.changedValues, key)) delete this.changedValues[key]
      } else {
        this.changedValues[key] = value
      }
      this.isDirty = Object.keys(this.changedValues).length > 0
      this.$emit('dirty-change', { isDirty: this.isDirty, changes: { ...this.changedValues } })
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
      if (this.isSubmitting) return
      if (!this.validateForm()) {
        return
      }
      
      this.isSubmitting = true
      
      try {
        await this.$emit('submit', { ...this.changedValues, __full: { ...this.formData } })
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
        this.changedValues = {}
        this.isDirty = false
        this.$emit('dirty-change', { isDirty: false, changes: {} })
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
/* Using PrimeFlex/PrimeVue for layout and spacing; no custom CSS needed here. */
</style>
