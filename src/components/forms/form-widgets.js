// components/forms/form-widgets.js
import TextInput from '@/components/inputs/TextInput.vue'
import SelectInput from '@/components/inputs/SelectInput.vue'
import MultiSelect from '@/components/inputs/MultiSelect.vue'
import Autocomplete from '@/components/inputs/Autocomplete.vue'
import Slider from '@/components/inputs/Slider.vue'
import DateInput from '@/components/inputs/DateInput.vue'
import FileUpload from '@/components/inputs/FileUpload.vue'
import JsonEditor from '@/components/inputs/JsonEditor.vue'

export const FORM_WIDGETS = {
  'text': {
    component: TextInput,             // Actual Vue component import
    defaultProps: { 
      placeholder: 'Enter text',
      class: 'w-full'
    }
  },
  'select': {
    component: SelectInput,           // Actual Vue component import
    defaultProps: { 
      placeholder: 'Select option',
      class: 'w-full'
    }
  },
  'multi_select': {
    component: MultiSelect,           // Actual Vue component import
    defaultProps: { 
      placeholder: 'Select options',
      class: 'w-full'
    }
  },
  'autocomplete': {
    component: Autocomplete,          // Actual Vue component import
    defaultProps: { 
      placeholder: 'Type to search',
      minLength: 2,
      delay: 300
    }
  },
  'slider': {
    component: Slider,                // Actual Vue component import
    defaultProps: { 
      min: 0,
      max: 100,
      step: 1
    }
  },
  'date': {
    component: DateInput,             // Actual Vue component import
    defaultProps: { 
      dateFormat: 'yy-mm-dd',
      class: 'w-full'
    }
  },
  'file': {
    component: FileUpload,            // Actual Vue component import
    defaultProps: { 
      multiple: false,
      accept: '*'
    }
  },
  'json': {
    component: JsonEditor,            // Actual Vue component import
    defaultProps: { 
      height: '200px',
      readOnly: false
    }
  }
}
