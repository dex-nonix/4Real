# 🧩 Widget Management System

## 🎯 **CORE CONCEPT:**
**ONE generic base class that handles different widget maps for different contexts (forms, table cells, etc.)**

## 🏗️ **ARCHITECTURE:**

### **1. BaseWidgetManager (Generic Base Class)**
```javascript
// BaseWidgetManager.js - GENERIC base class!
class BaseWidgetManager {
  constructor(widgetMap = {}) {
    this.widgets = widgetMap
  }

  // Get widget with resolved props
  getWidget(type, userProps = {}) {
    const widget = this.widgets[type]
    if (!widget) return this.getDefaultWidget() // fallback
    
    return {
      component: widget.component,
      props: { ...widget.defaultProps, ...userProps }
    }
  }

  // Register new widget
  registerWidget(type, component, defaultProps = {}) {
    this.widgets[type] = { component, defaultProps }
  }

  // Get available widget types
  getAvailableTypes() {
    return Object.keys(this.widgets)
  }

  // Abstract method - subclasses must implement
  getDefaultWidget() {
    throw new Error('Subclasses must implement getDefaultWidget()')
  }
}
```

### **2. Widget Mappings (Separate Config Files)**
```javascript
// widget-mappings/form-widgets.js
export const FORM_WIDGETS = {
  'text': {
    component: TextInput,
    defaultProps: { placeholder: 'Enter text', maxLength: 255 }
  },
  'select': {
    component: SelectInput,
    defaultProps: { placeholder: 'Select option', clearable: true }
  },
  'multi_select': {
    component: MultiSelect,
    defaultProps: { placeholder: 'Select options', multiple: true }
  },
  'autocomplete': {
    component: Autocomplete,
    defaultProps: { placeholder: 'Type to search', minLength: 2, delay: 300 }
  },
  'slider': {
    component: Slider,
    defaultProps: { min: 0, max: 100, step: 1 }
  },
  'date': {
    component: DateInput,
    defaultProps: { placeholder: 'Select date', format: 'YYYY-MM-DD' }
  },
  'file': {
    component: FileUpload,
    defaultProps: { multiple: false, accept: '*' }
  },
  'json': {
    component: JsonEditor,
    defaultProps: { height: '200px', readOnly: false }
  }
}

// widget-mappings/table-widgets.js  
export const TABLE_WIDGETS = {
  'text': {
    component: TextCell,
    defaultProps: { truncate: true, maxLength: 50 }
  },
  'date': {
    component: DateCell,
    defaultProps: { format: 'YYYY-MM-DD' }
  },
  'status': {
    component: StatusCell,
    defaultProps: { showIcon: true }
  },
  'actions': {
    component: ActionCell,
    defaultProps: { showEdit: true, showDelete: true }
  }
}
```

### **3. Specific Widget Managers (Extend Base Class)**
```javascript
// FormWidgetManager - for form inputs!
import { FORM_WIDGETS } from '@/widget-mappings/form-widgets.js'

class FormWidgetManager extends BaseWidgetManager {
  constructor() {
    super(FORM_WIDGETS) // Pass the imported mapping!
  }

  getDefaultWidget() {
    return { component: TextInput, props: { placeholder: 'Enter text' } }
  }
}

// TableCellWidgetManager - for table cell rendering!
import { TABLE_WIDGETS } from '@/widget-mappings/table-widgets.js'

class TableCellWidgetManager extends BaseWidgetManager {
  constructor() {
    super(TABLE_WIDGETS) // Pass the imported mapping!
  }

  getDefaultWidget() {
    return { component: TextCell, props: { truncate: true } }
  }
}
```

## 🔧 **USAGE PATTERNS:**

### **1. Form Widgets (DynamicForm.vue)**
```javascript
// In DynamicForm.vue
import { FormWidgetManager } from '@/widgets/FormWidgetManager.js'

const formManager = new FormWidgetManager()

// Get widget with user props
const { component, props } = formManager.getWidget('multi_select', { 
  options: [], 
  placeholder: 'Choose albums' 
})

// User props override defaults
// Default: { placeholder: 'Select options', multiple: true }
// Result: { placeholder: 'Choose albums', multiple: true, options: [] }
```

### **2. Table Cell Widgets (DynamicTable.vue)**
```javascript
// In DynamicTable.vue
import { TableCellWidgetManager } from '@/widgets/TableCellWidgetManager.js'

const tableManager = new TableCellWidgetManager()

// Get cell widget
const { component, props } = tableManager.getWidget('date', { 
  format: 'MM/DD/YYYY' 
})

// User format overrides default
// Default: { format: 'YYYY-MM-DD' }
// Result: { format: 'MM/DD/YYYY' }
```

### **3. CRUD Config Integration**
```javascript
// artist-crud-config.js
export const artistCrudConfig = {
  entity: 'artist',
  form: {
    fields: {
      name: {
        type: 'text',                    // Maps to TextInput
        label: 'Artist Name',
        required: true,
        props: {                         // PROPS PROPERTY!
          placeholder: 'Enter artist name',
          maxLength: 100
        }
      },
      albums: {
        type: 'multi_select',            // Maps to MultiSelect
        label: 'Albums',
        props: {                         // PROPS PROPERTY!
          options: [],                   // Will be populated from API
          placeholder: 'Choose albums'   // Override default placeholder
        }
      }
    }
  }
}
```

## 📁 **FILE STRUCTURE:**
```
frontend/src/
├── widgets/
│   ├── BaseWidgetManager.js           # Generic base class
│   ├── FormWidgetManager.js           # Form-specific manager
│   ├── TableCellWidgetManager.js      # Table-specific manager
│   └── widget-mappings/               # Widget configuration files
│       ├── form-widgets.js            # Form widget mappings
│       ├── table-widgets.js           # Table widget mappings
│       └── dashboard-widgets.js       # Dashboard widget mappings (future)
├── components/
│   ├── core/
│   │   ├── DynamicForm.vue            # Uses FormWidgetManager
│   │   └── DynamicTable.vue           # Uses TableCellWidgetManager
│   └── inputs/                        # Actual widget components
│       ├── TextInput.vue
│       ├── MultiSelect.vue
│       └── ...
```

## 🎯 **KEY BENEFITS:**

### **✅ DRY Architecture:**
- **One base class** handles all widget management logic
- **Different managers** for different contexts (forms, tables, etc.)
- **Reusable** across all components

### **✅ Clean Separation:**
- **Widget mappings** in separate config files
- **Classes** just import and use mappings
- **Easy to maintain** and extend

### **✅ Flexible Configuration:**
- **Default props** provide sensible behavior
- **User props** override defaults when needed
- **No hardcoded values** scattered in components

### **✅ Extensible System:**
- **Add new widget types** by updating config files
- **Add new contexts** by extending BaseWidgetManager
- **Register widgets** dynamically at runtime

## 🚫 **WHAT WE DON'T DO:**

### **❌ No Multiple Classes:**
- **No WidgetRegistry.js** - unnecessary
- **No widgetConfigs.js** - mappings are in separate files
- **No widgetFactory.js** - Vue components don't need factories

### **❌ No Hardcoded Mappings:**
- **No inline mappings** in constructors
- **No scattered widget definitions** across classes
- **No duplicate mapping logic** in different managers

### **❌ No Complex Abstractions:**
- **No "widget" vs "component" confusion** - everything is a Vue component
- **No unnecessary abstraction layers** - just clean mapping and resolution
- **No over-engineering** - simple, working solution

## 🔄 **WORKFLOW:**

1. **Define widget mappings** in separate config files
2. **Create specific managers** that extend BaseWidgetManager
3. **Pass mappings** to managers via constructor
4. **Use managers** in components to resolve widgets
5. **Merge default props** with user props for final configuration

**This gives us ONE generic system that handles ALL widget management needs without over-engineering!**
