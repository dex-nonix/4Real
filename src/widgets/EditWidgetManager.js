// src/widgets/EditWidgetManager.js
import BaseWidgetManager from '@/widgets/BaseWidgetManager.js'
import { EDIT_WIDGETS } from '@/widgets/edit-widgets.js'

class EditWidgetManager extends BaseWidgetManager {
  constructor() {
    super(EDIT_WIDGETS)
  }

  getDefaultWidget() {
    return { component: 'input', props: { class: 'w-full' } }
  }
}

export default EditWidgetManager


