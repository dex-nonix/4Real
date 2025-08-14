import BaseWidgetManager from '@/libs/core/widget-manager/BaseWidgetManager.js'
import { EDIT_WIDGETS } from '@/libs/core/registries/edit-widgets.js'

class EditWidgetManager extends BaseWidgetManager {
  constructor() {
    super(EDIT_WIDGETS)
  }

  getDefaultWidget() {
    return { component: 'input', props: { class: 'w-full' } }
  }
}

export default EditWidgetManager


