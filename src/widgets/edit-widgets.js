// src/widgets/edit-widgets.js
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import AutoComplete from 'primevue/autocomplete'
import Slider from 'primevue/slider'
import InputSwitch from 'primevue/inputswitch'
import Calendar from 'primevue/calendar'
import FileUpload from 'primevue/fileupload'
import Editor from 'primevue/editor'
import { ref, inject, h } from 'vue'
import CrudService from '@/services/CrudService.js'
import FileUploadField from '@/components/widgets/FileUploadField.vue'

export const EDIT_WIDGETS = {
  'text': { component: InputText, defaultProps: { placeholder: 'Enter text', class: 'w-full' } },
  'select': { component: Dropdown, defaultProps: { placeholder: 'Select option', class: 'w-full' } },
  'multi_select': { component: MultiSelect, defaultProps: { placeholder: 'Select options', class: 'w-full' } },
  'autocomplete': { component: AutoComplete, defaultProps: { placeholder: 'Type to search', minLength: 2, delay: 300 } },
  'slider': { component: Slider, defaultProps: { min: 0, max: 100, step: 1 } },
  'date': { component: Calendar, defaultProps: { dateFormat: 'yy-mm-dd', class: 'w-full' } },
  'file': { component: FileUpload, defaultProps: { multiple: false, accept: '*' } },
  'json': { component: Editor, defaultProps: { height: '200px', readOnly: false } },
  'boolean': { component: InputSwitch, defaultProps: { class: 'block' } }
}

// Minimal FK helper component factories
function createFkSelect() {
  return {
    props: {
      modelValue: [Number, String, Array],
      entity: { type: String, required: true },
      valueKey: { type: String, default: 'id' },
      labelKey: { type: String, default: 'label' },
      placeholder: { type: String, default: 'Select...' },
      clearable: { type: Boolean, default: true },
      disabled: { type: Boolean, default: false },
      search: { type: Boolean, default: false },
      debounceMs: { type: Number, default: 250 },
      params: { type: Object, default: () => ({}) },
      resolveOnMount: { type: Boolean, default: true },
      multiple: { type: Boolean, default: false }
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const injected = inject(props.entity)
      const service = injected || new CrudService(props.entity)
      const options = ref([])
      const selected = ref(props.modelValue)
      let timer = null

      async function loadInitial() {
        try {
          if (props.resolveOnMount && props.modelValue != null && !props.multiple) {
            const res = await service.selectorGet(props.modelValue)
            const item = res?.data?.data || res?.data
            if (item) options.value = [item]
          } else {
            const res = await service.selectorList(props.params)
            options.value = res?.data?.data || res?.data || []
          }
        } catch {
          options.value = []
        }
      }

      function onSearch(q) {
        if (!props.search) return
        if (timer) clearTimeout(timer)
        timer = setTimeout(async () => {
          try {
            const res = await service.selectorList({ ...props.params, q })
            options.value = res?.data?.data || res?.data || []
          } catch { /* noop */ }
        }, props.debounceMs)
      }

      function update(val) { emit('update:modelValue', val) }

      loadInitial()

      return { options, selected, onSearch, update }
    },
    render() {
      const commonProps = {
        class: 'w-full',
        options: this.options,
        optionLabel: this.labelKey,
        optionValue: this.valueKey,
        placeholder: this.placeholder,
        disabled: this.disabled,
        showClear: this.clearable,
        modelValue: this.modelValue,
        'onUpdate:modelValue': this.update
      }
      if (!this.multiple) {
        return h(Dropdown, {
          ...commonProps,
          filter: this.search,
          filterBy: this.labelKey,
          onFilter: this.onSearch
        })
      }
      return h(MultiSelect, commonProps)
    }
  }
}

export const FK_SELECT = createFkSelect()
export const FK_MULTI_SELECT = createFkSelect()

// Register FK widgets
EDIT_WIDGETS['fk_select'] = { component: FK_SELECT, defaultProps: {} }
EDIT_WIDGETS['fk_autocomplete'] = { component: FK_SELECT, defaultProps: { search: true } }
EDIT_WIDGETS['fk_multi_select'] = { component: FK_MULTI_SELECT, defaultProps: { multiple: true } }
EDIT_WIDGETS['file_upload'] = { component: FileUploadField, defaultProps: { buttonLabel: 'Choose File' } }


