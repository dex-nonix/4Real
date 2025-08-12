// components/tables/table-widgets.js
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'

export const TABLE_WIDGETS = {
  'text': {
    component: 'span',                // Simple span for text (HTML element)
    defaultProps: { 
      class: 'text-sm'
    }
  },
  'number': {
    component: 'span',                // Formatted number display (HTML element)
    defaultProps: { 
      class: 'text-sm font-mono'
    }
  },
  'date': {
    component: 'span',                // Formatted date display (HTML element)
    defaultProps: { 
      class: 'text-sm text-gray-600'
    }
  },
  'status': {
    component: Tag,                   // PrimeVue Tag component import
    defaultProps: { 
      severity: 'info'
    }
  },
  'actions': {
    component: Button,                // PrimeVue Button component import
    defaultProps: { 
      size: 'small',
      severity: 'secondary'
    }
  },
  'image': {
    component: Avatar,                // PrimeVue Avatar component import
    defaultProps: { 
      size: 'normal',
      shape: 'circle'
    }
  },
  'boolean': {
    component: 'i',                   // Icon for boolean values (HTML element)
    defaultProps: { 
      class: 'pi',
      style: 'font-size: 1.2rem;'
    }
  }
}
