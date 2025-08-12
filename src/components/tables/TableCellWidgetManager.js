// TableCellWidgetManager - for table cell rendering!
import BaseWidgetManager from '../../widgets/BaseWidgetManager.js'
import { TABLE_WIDGETS } from './table-widgets.js'

class TableCellWidgetManager extends BaseWidgetManager {
  constructor() {
    super(TABLE_WIDGETS) // Pass the imported mapping!
  }

  getDefaultWidget() {
    return { component: 'span', props: { class: 'text-sm' } }
  }
}

export default TableCellWidgetManager
