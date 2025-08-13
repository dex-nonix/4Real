// src/widgets/display-widgets.js
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'

export const DISPLAY_WIDGETS = {
  'text': { component: 'span', defaultProps: { class: 'text-sm' } },
  'number': { component: 'span', defaultProps: { class: 'text-sm font-mono' } },
  'date': { component: 'span', defaultProps: { class: 'text-sm text-gray-600' } },
  'status': { component: Tag, defaultProps: { severity: 'info' } },
  'actions': { component: Button, defaultProps: { size: 'small', severity: 'secondary' } },
  'image': { component: Avatar, defaultProps: { size: 'normal', shape: 'circle' } },
  'boolean': { component: 'i', defaultProps: { class: 'pi', style: 'font-size: 1.2rem;' } }
}


