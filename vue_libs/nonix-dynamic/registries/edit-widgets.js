import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import AutoComplete from 'primevue/autocomplete'
import Slider from 'primevue/slider'
import InputSwitch from 'primevue/inputswitch'
import Calendar from 'primevue/calendar'
import FileUpload from 'primevue/fileupload'
import Editor from 'primevue/editor'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import { ref, inject, h } from 'vue'
import NxCrudService from '@nonix-crud/services/NxCrudService.js'
import NxFileUploadField from '@nonix-file-manager/components/NxFileUploadField.vue'
import NxLlmTool from '@nonix-chat/widgets/NxLlmTool.vue'

export const NX_EDIT_WIDGETS = {
  'text': { component: InputText, defaultProps: { placeholder: 'Enter text', class: 'w-full' } },
  'textarea': { component: Textarea, defaultProps: { autoResize: true, class: 'w-full', rows: 5 } },
  'select': { component: Dropdown, defaultProps: { placeholder: 'Select option', class: 'w-full' } },
  'multi_select': { component: MultiSelect, defaultProps: { placeholder: 'Select options', class: 'w-full' } },
  'autocomplete': { component: AutoComplete, defaultProps: { placeholder: 'Type to search', minLength: 2, delay: 300 } },
  'slider': { component: Slider, defaultProps: { min: 0, max: 100, step: 1 } },
  'date': { component: Calendar, defaultProps: { dateFormat: 'yy-mm-dd', class: 'w-full' } },
  'file': { component: FileUpload, defaultProps: { multiple: false, accept: '*' } },
  // Dedicated markdown editor (rich text). Use this only for markdown fields
  'markdown': { component: Editor, defaultProps: { height: '220px', readOnly: false } },
  // JSON editor: textarea with validation and format helper
  'json': { component: {
    props: { modelValue: [Object, Array, String, null] },
    emits: ['update:modelValue'],
    data() {
      let start = ''
      try {
        if (this.modelValue != null && typeof this.modelValue !== 'string') {
          start = JSON.stringify(this.modelValue, null, 2)
        } else if (typeof this.modelValue === 'string') {
          start = this.modelValue
        }
      } catch { start = '' }
      return { text: start, error: '' }
    },
    methods: {
      onInput(e) {
        this.text = e?.target?.value ?? ''
        try {
          const parsed = this.text ? JSON.parse(this.text) : null
          this.error = ''
          this.$emit('update:modelValue', parsed)
        } catch (err) {
          this.error = 'Invalid JSON'
        }
      },
      format() {
        try {
          const obj = this.text ? JSON.parse(this.text) : null
          this.text = obj != null ? JSON.stringify(obj, null, 2) : ''
          this.error = ''
          this.$emit('update:modelValue', obj)
        } catch {
          this.error = 'Invalid JSON'
        }
      }
    },
    render() {
      return h('div', { class: 'flex flex-column gap-2 w-full' }, [
        h(Textarea, { modelValue: this.text, 'onUpdate:modelValue': v => this.onInput({ target: { value: v } }), class: 'w-full font-mono', autoResize: true, rows: 8 }),
        h('div', { class: 'flex align-items-center justify-content-between' }, [
          h('small', { class: this.error ? 'p-error' : 'invisible' }, this.error || '\u00A0'),
          h(Button, { label: 'Format', size: 'small', onClick: this.format })
        ])
      ])
    }
  }, defaultProps: {} },
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
      const service = injected || new NxCrudService(props.entity)
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

export const NX_FK_SELECT = createFkSelect()
export const NX_FK_MULTI_SELECT = createFkSelect()

// Register FK widgets
NX_EDIT_WIDGETS['fk_select'] = { component: NX_FK_SELECT, defaultProps: {} }
NX_EDIT_WIDGETS['fk_autocomplete'] = { component: NX_FK_SELECT, defaultProps: { search: true } }
NX_EDIT_WIDGETS['fk_multi_select'] = { component: NX_FK_MULTI_SELECT, defaultProps: { multiple: true } }
NX_EDIT_WIDGETS['file_upload'] = { component: NxFileUploadField, defaultProps: { buttonLabel: 'Choose File' } }
NX_EDIT_WIDGETS['llm_tool'] = { component: NxLlmTool, defaultProps: { allowWildcards: true, placeholder: 'Select or type a tool' } }


