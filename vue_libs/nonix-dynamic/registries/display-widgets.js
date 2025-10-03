import Tag from 'primevue/tag'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import { ref, inject, h } from 'vue'
import NxCrudService from '@nonix-crud/services/NxCrudService.js'
import NxFilePreview from '@nonix-file-manager/components/NxFilePreview.vue'
import NxLlmTool from '@nonix-chat/widgets/NxLlmTool.vue'

export const NX_DISPLAY_WIDGETS = {
  'text': { component: 'span', defaultProps: { class: 'text-sm' } },
  'number': { component: 'span', defaultProps: { class: 'text-sm font-mono' } },
  'date': { component: 'span', defaultProps: { class: 'text-sm text-gray-600' } },
  'status': { component: Tag, defaultProps: { severity: 'info' } },
  'actions': { component: Button, defaultProps: { size: 'small', severity: 'secondary' } },
  'image': { component: Avatar, defaultProps: { size: 'normal', shape: 'circle' } },
  'boolean': { component: {
    props: { value: [Boolean, Number, String] },
    render() {
      const truthy = this.value === true || this.value === 1 || this.value === '1'
      return h('i', { class: `pi ${truthy ? 'pi-check text-green-500' : 'pi-times text-red-500'}`, style: 'font-size: 1.2rem;' })
    }
  }, defaultProps: {} },
  'file_preview': { component: NxFilePreview, defaultProps: { } },
  'json': { component: {
    props: { value: [Object, Array, String, null] },
    render() {
      let text = ''
      try {
        if (typeof this.value === 'string') text = this.value
        else if (this.value != null) text = JSON.stringify(this.value, null, 2)
      } catch { text = '' }
      return h('pre', { class: 'text-sm font-mono whitespace-pre-wrap' }, text)
    }
  }, defaultProps: {} },
  'file_preview_fk': { component: {
    props: { value: [Number, String], entity: { type: String, default: 'files' }, labelKey: { type: String, default: 'label' } },
    setup(props) {
      const injected = inject(props.entity)
      const service = injected || new NxCrudService(props.entity)
      const data = ref(null)
      const load = async (id) => {
        try {
          const res = await service.get(id)
          const obj = res?.data?.data || res?.data
          data.value = obj || null
        } catch { data.value = null }
      }
      if (props.value != null) load(props.value)
      return { data }
    },
    render() {
      const file = this.data || {}
      return h(NxFilePreview, { value: file, url: file.storage_url, mime: file.mime_type, title: file.title, filename: file.original_filename })
    }
  }, defaultProps: {} },
  'fk_display': { component: {
    props: { value: [Number, String, Array], entity: { type: String, required: true }, labelKey: { type: String, default: 'label' } },
    setup(props) {
      const injected = inject(props.entity)
      const service = injected || new NxCrudService(props.entity)
      const label = ref('')
      const resolve = async (id) => {
        try {
          const res = await service.selectorGet(id)
          const item = res?.data?.data || res?.data
          label.value = item?.[props.labelKey] || ''
        } catch { label.value = '' }
      }
      if (Array.isArray(props.value)) {
        label.value = ''
      } else if (props.value != null) {
        resolve(props.value)
      }
      return { label }
    },
    render() { return h('span', this.label) }
  }, defaultProps: {} }
  ,
  'llm_tool': { component: NxLlmTool, defaultProps: { mode: 'display' } },
  'mcp_connection': { component: {
    props: { value: [String, null], rowData: { type: Object, default: () => ({}) } },
    render() {
      const transport = this.rowData.transport || 'stdio'
      const displayValue = transport === 'stdio' ? this.rowData.command : this.rowData.url
      return h('span', { class: 'text-sm' }, displayValue || '')
    }
  }, defaultProps: {} }
}


