// components/forms/form-widgets.js
import { InputText } from 'primevue/inputtext'
import { Dropdown } from 'primevue/dropdown'
import { MultiSelect } from 'primevue/multiselect'
import { AutoComplete } from 'primevue/autocomplete'
import { Slider } from 'primevue/slider'
import { Calendar } from 'primevue/calendar'
import { FileUpload } from 'primevue/fileupload'
import { Editor } from 'primevue/editor'

export const FORM_WIDGETS = {
  'text': {
    component: InputText,             // PrimeVue InputText component
    defaultProps: { 
      placeholder: 'Enter text',
      class: 'w-full'
    }
  },
  'select': {
    component: Dropdown,              // PrimeVue Dropdown component
    defaultProps: { 
      placeholder: 'Select option',
      class: 'w-full'
    }
  },
  'multi_select': {
    component: MultiSelect,           // PrimeVue MultiSelect component
    defaultProps: { 
      placeholder: 'Select options',
      class: 'w-full'
    }
  },
  'autocomplete': {
    component: AutoComplete,          // PrimeVue AutoComplete component
    defaultProps: { 
      placeholder: 'Type to search',
      minLength: 2,
      delay: 300
    }
  },
  'slider': {
    component: Slider,                // PrimeVue Slider component
    defaultProps: { 
      min: 0,
      max: 100,
      step: 1
    }
  },
  'date': {
    component: Calendar,              // PrimeVue Calendar component
    defaultProps: { 
      dateFormat: 'yy-mm-dd',
      class: 'w-full'
    }
  },
  'file': {
    component: FileUpload,            // PrimeVue FileUpload component
    defaultProps: { 
      multiple: false,
      accept: '*'
    }
  },
  'json': {
    component: Editor,                // PrimeVue Editor component
    defaultProps: { 
      height: '200px',
      readOnly: false
    }
  }
}
