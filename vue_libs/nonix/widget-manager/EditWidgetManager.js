import BaseWidgetManager from '@nonix/widget-manager/BaseWidgetManager.js'
import { EDIT_WIDGETS } from '@nonix/registries/edit-widgets.js'

class EditWidgetManager extends BaseWidgetManager {
  constructor() {
    super(EDIT_WIDGETS)
  }

  getDefaultWidget() {
    return { component: 'input', props: { class: 'w-full' } }
  }
}

export default EditWidgetManager


