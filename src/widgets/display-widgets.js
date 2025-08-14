// src/widgets/display-widgets.js
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import { ref, inject, h } from 'vue'
import CrudService from '@/services/CrudService.js'
import FilePreview from '@/components/widgets/FilePreview.vue'

export const DISPLAY_WIDGETS = {
  'text': { component: 'span', defaultProps: { class: 'text-sm' } },
  'number': { component: 'span', defaultProps: { class: 'text-sm font-mono' } },
  'date': { component: 'span', defaultProps: { class: 'text-sm text-gray-600' } },
  'status': { component: Tag, defaultProps: { severity: 'info' } },
  'actions': { component: Button, defaultProps: { size: 'small', severity: 'secondary' } },
  'image': { component: Avatar, defaultProps: { size: 'normal', shape: 'circle' } },
  'boolean': { component: 'i', defaultProps: { class: 'pi', style: 'font-size: 1.2rem;' } },
  'file_preview': { component: FilePreview, defaultProps: { } },
  'fk_display': { component: {
    props: { value: [Number, String, Array], entity: { type: String, required: true }, labelKey: { type: String, default: 'label' } },
    setup(props) {
      const injected = inject(props.entity)
      const service = injected || new CrudService(props.entity)
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
}


