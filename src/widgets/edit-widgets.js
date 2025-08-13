// src/widgets/edit-widgets.js
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import AutoComplete from 'primevue/autocomplete'
import Slider from 'primevue/slider'
import Calendar from 'primevue/calendar'
import FileUpload from 'primevue/fileupload'
import Editor from 'primevue/editor'

export const EDIT_WIDGETS = {
  'text': { component: InputText, defaultProps: { placeholder: 'Enter text', class: 'w-full' } },
  'select': { component: Dropdown, defaultProps: { placeholder: 'Select option', class: 'w-full' } },
  'multi_select': { component: MultiSelect, defaultProps: { placeholder: 'Select options', class: 'w-full' } },
  'autocomplete': { component: AutoComplete, defaultProps: { placeholder: 'Type to search', minLength: 2, delay: 300 } },
  'slider': { component: Slider, defaultProps: { min: 0, max: 100, step: 1 } },
  'date': { component: Calendar, defaultProps: { dateFormat: 'yy-mm-dd', class: 'w-full' } },
  'file': { component: FileUpload, defaultProps: { multiple: false, accept: '*' } },
  'json': { component: Editor, defaultProps: { height: '200px', readOnly: false } }
}


