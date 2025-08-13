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

### **2. Widget Registry Pattern**
The BaseWidgetManager expects a widget map structure like this:

```javascript
// Generic widget map structure (example)
export const WIDGET_MAP = {
  'widget_type': {
    component: ActualComponent,        // Vue component or HTML element
    defaultProps: { 
      // Default properties for this widget
      class: 'default-class',
      placeholder: 'Default text'
    }
  }
}
```

### **3. Specific Widget Managers (Extend Base Class)**
Specific contexts create their own managers by extending BaseWidgetManager:

```javascript
// Example: FormWidgetManager extends BaseWidgetManager
class FormWidgetManager extends BaseWidgetManager {
  constructor() {
    super(FORM_WIDGETS) // Pass the imported mapping!
  }

  getDefaultWidget() {
    return { component: 'InputText', props: { placeholder: 'Enter text' } }
  }
}

// Example: TableCellWidgetManager extends BaseWidgetManager  
class TableCellWidgetManager extends BaseWidgetManager {
  constructor() {
    super(TABLE_WIDGETS) // Pass the imported mapping!
  }

  getDefaultWidget() {
    return { component: 'span', props: { class: 'text-sm' } }
  }
}
```

## 📁 **FILE STRUCTURE:**
```
src/
├── components/                     # All components
│   ├── forms/                      # Form components
│   │   ├── DynamicForm.vue         # Form renderer
│   │   ├── FormWidgetManager.js    # Form widget manager (INSIDE forms folder!)
│   │   └── form-widgets.js         # Form widget registry
│   ├── tables/                     # Table components
│   │   ├── DynamicTable.vue        # Table renderer
│   │   ├── TableCellWidgetManager.js # Table widget manager (INSIDE tables folder!)
│   │   └── table-widgets.js        # Table widget registry
│   ├── crud/                       # CRUD operations
│   │   └── CrudManager.vue         # Complete CRUD component
│   ├── inputs/                     # Input widgets
│   ├── actions/                    # Action components
│   └── dialogs/                    # Dialog components
├── views/                           # Page views
├── services/                        # API services
└── utils/                           # Utility functions
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

- **DynamicForm.md** - Form component using FormWidgetManager + form-widgets.js registry
- **DynamicTable.md** - Table component using TableCellWidgetManager + table-widgets.js registry
- **CrudManager.md** - CRUD component using both managers

**This gives us ONE generic system that handles ALL widget management needs without over-engineering. Use PrimeVue components and PrimeFlex utilities for layout/spacing — avoid custom CSS unless truly unavoidable.**
