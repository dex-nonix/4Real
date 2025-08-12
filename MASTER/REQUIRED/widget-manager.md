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
    component: 'InputText',           // PrimeVue component
    defaultProps: { 
      placeholder: 'Enter text',
      class: 'w-full'
    }
  },
  'select': {
    component: 'Dropdown',            // PrimeVue component
    defaultProps: { 
      placeholder: 'Select option',
      class: 'w-full'
    }
  },
  'multi_select': {
    component: 'MultiSelect',         // PrimeVue component
    defaultProps: { 
      placeholder: 'Select options',
      class: 'w-full'
    }
  },
  'autocomplete': {
    component: 'AutoComplete',        // PrimeVue component
    defaultProps: { 
      placeholder: 'Type to search',
      minLength: 2,
      delay: 300
    }
  },
  'slider': {
    component: 'Slider',              // PrimeVue component
    defaultProps: { 
      min: 0,
      max: 100,
      step: 1
    }
  },
  'date': {
    component: 'Calendar',            // PrimeVue component
    defaultProps: { 
      dateFormat: 'yy-mm-dd',
      class: 'w-full'
    }
  },
  'file': {
    component: 'FileUpload',          // PrimeVue component
    defaultProps: { 
      multiple: false,
      accept: '*'
    }
  },
  'json': {
    component: 'Editor',              // PrimeVue component
    defaultProps: { 
      height: '200px',
      readOnly: false
    }
  }
}

// widget-mappings/table-widgets.js  
export const TABLE_WIDGETS = {
  'text': {
    component: 'span',                // Simple span for text
    defaultProps: { 
      class: 'text-sm'
    }
  },
  'number': {
    component: 'span',                // Formatted number display
    defaultProps: { 
      class: 'text-sm font-mono'
    }
  },
  'date': {
    component: 'span',                // Formatted date display
    defaultProps: { 
      class: 'text-sm text-gray-600'
    }
  },
  'status': {
    component: 'Tag',                 // PrimeVue Tag component
    defaultProps: { 
      severity: 'info'
    }
  },
  'actions': {
    component: 'Button',              // PrimeVue Button
    defaultProps: { 
      size: 'small',
      severity: 'secondary'
    }
  },
  'image': {
    component: 'Avatar',              // PrimeVue Avatar
    defaultProps: { 
      size: 'normal',
      shape: 'circle'
    }
  },
  'boolean': {
    component: 'i',                   // Icon for boolean values
    defaultProps: { 
      class: 'pi',
      style: 'font-size: 1.2rem;'
    }
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
    return { component: 'InputText', props: { placeholder: 'Enter text' } }
  }
}

// TableCellWidgetManager - for table cell rendering!
import { TABLE_WIDGETS } from '@/widget-mappings/table-widgets.js'

class TableCellWidgetManager extends BaseWidgetManager {
  constructor() {
    super(TABLE_WIDGETS) // Pass the imported mapping!
  }

  getDefaultWidget() {
    return { component: 'span', props: { class: 'text-sm' } }
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
// Default: { placeholder: 'Select options', class: 'w-full' }
// Result: { placeholder: 'Choose albums', class: 'w-full', options: [] }
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
// Default: { class: 'text-sm text-gray-600' }
// Result: { class: 'text-sm text-gray-600', format: 'MM/DD/YYYY' }
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
│   └── crud/
│       └── CrudManager.vue            # Uses both managers
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

## 📚 **RELATED DOCUMENTATION:**

- **DynamicForm.md** - Form component using FormWidgetManager
- **DynamicTable.md** - Table component using TableCellWidgetManager  
- **CrudManager.md** - CRUD component using both managers

**This gives us ONE generic system that handles ALL widget management needs without over-engineering!**
