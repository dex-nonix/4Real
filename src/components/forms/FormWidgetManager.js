// FormWidgetManager - for form inputs!
import BaseWidgetManager from '@/widgets/BaseWidgetManager.js'
import { FORM_WIDGETS } from '@/components/forms/form-widgets.js'

class FormWidgetManager extends BaseWidgetManager {
  constructor() {
    super(FORM_WIDGETS) // Pass the imported mapping!
  }

  getDefaultWidget() {
    return { component: 'InputText', props: { placeholder: 'Enter text' } }
  }
}

export default FormWidgetManager
