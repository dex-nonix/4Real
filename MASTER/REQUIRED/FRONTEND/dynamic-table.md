# 📊 DynamicTable Component

## 🎯 **PURPOSE:**
**Generic table component that uses the widget manager system to render any data table with custom cell widgets - works for CRUD, dashboards, inline tables, etc.**

## 🏗️ **ARCHITECTURE:**

### **Core Concept:**
- **Configuration-driven tables** - no hardcoded table layouts
- **Widget manager integration** - uses DisplayWidgetManager for cell rendering
- **Generic data handling** - works with any data structure
- **Custom cell widgets** - different rendering for different data types
- **Flexible layouts** - vertical (default), horizontal, compact for different use cases
- **Responsive support** - hide columns based on screen size

### **DisplayWidgetManager Integration:**
The DynamicTable component uses the **DisplayWidgetManager** class to resolve and render table cell widgets. The DisplayWidgetManager:

- **Extends BaseWidgetManager** - inherits generic widget management capabilities
- **Manages display widgets** - text displays, status tags, action buttons, etc.
- **Handles default props** - provides sensible defaults for each cell type
- **Allows prop overrides** - user props can override default cell behavior
- **Co-located with table component** - lives in the same `components/tables/` folder

#### **How DisplayWidgetManager Works:**
```javascript
// In DynamicTable.vue
data() {
  return {
    tableManager: new DisplayWidgetManager(),
    // ... other data
  }
},

methods: {
  // Resolve cell widget using DisplayWidgetManager
  resolveCellWidget(type) {
    return this.tableManager.getWidget(type, {}, null) // Gets widget with default props
  }
}
```

 

The TableCellWidgetManager automatically resolves cell types like `'text'`, `'status'`, `'actions'`, `'date'` to their corresponding components (span, Tag, Button, etc.) and applies default styling and behavior for consistent table cell rendering. PrimeVue components are used directly; no custom input wrappers needed.

### **Display Widget Registry (display-widgets.js):**
The DisplayWidgetManager uses a registry file that maps cell types to actual components:

```javascript
// widgets/display-widgets.js
import { Tag } from 'primevue/tag'
import { Button } from 'primevue/button'
import { Avatar } from 'primevue/avatar'

export const DISPLAY_WIDGETS = {
  'text': {
    component: 'span',                // Simple span for text (HTML element)
    defaultProps: { 
      class: 'text-sm'
    }
  },
  'number': {
    component: 'span',                // Formatted number display (HTML element)
    defaultProps: { 
      class: 'text-sm font-mono'
    }
  },
  'date': {
    component: 'span',                // Formatted date display (HTML element)
    defaultProps: { 
      class: 'text-sm text-gray-600'
    }
  },
  'status': {
    component: Tag,                   // PrimeVue Tag component import
    defaultProps: { 
      severity: 'info'
    }
  },
  'actions': {
    component: Button,                // PrimeVue Button component import
    defaultProps: { 
      size: 'small',
      severity: 'secondary'
    }
  },
  'image': {
    component: Avatar,                // PrimeVue Avatar component import
    defaultProps: { 
      size: 'normal',
      shape: 'circle'
    }
  },
  'boolean': {
    component: 'i',                   // Icon for boolean values (HTML element)
    defaultProps: { 
      class: 'pi',
      style: 'font-size: 1.2rem;'
    }
  }
}
```

This registry file lives in the same `components/tables/` folder as the DynamicTable component and TableCellWidgetManager.

## 🔧 **IMPLEMENTATION:**

### **1. DynamicTable.vue Component (Prime-first, no custom CSS):**
```vue
<template>
  <div class="dynamic-table" :class="tableClasses">
    <!-- Search and Filters -->
    <div v-if="config.filters && !minimal" class="table-filters flex align-items-center gap-3 mb-3">
      <SearchFilter 
        v-if="config.filters.includes('search')"
        v-model="searchQuery"
        placeholder="Search..."
        @search="handleSearch"
      />
      
      <DateRangeFilter 
        v-if="config.filters.includes('date_range')"
        v-model="dateRange"
        @change="handleDateFilter"
      />
    </div>
    
    <!-- Data Table -->
    <DataTable 
      :value="filteredData" 
      :columns="visibleColumns"
      :paginator="config.paginated && !minimal"
      :rows="config.pageSize || 10"
      :loading="loading"
      :sortable="config.sortable"
      :resizable-columns="config.resizable && !compact"
      :striped-rows="config.striped"
      :row-hover="config.hover"
      :selection-mode="config.selectionMode && !minimal ? config.selectionMode : null"
      v-model:selection="selectedRows"
      @row-select="handleRowSelect"
      @row-unselect="handleRowUnselect"
      :class="tableDataClasses"
    >
      <!-- Dynamic Column Rendering -->
      <Column 
        v-for="col in visibleColumns" 
        :key="col.field" 
        :field="col.field" 
        :header="col.header"
        :sortable="col.sortable !== false && !minimal"
        :filter="col.filter && !minimal"
        :filter-placeholder="col.filterPlaceholder"
        :style="col.style"
        :class="col.class"
      >
        <template #body="slotProps">
          <!-- Dynamic Cell Widget Rendering -->
          <component 
            :is="resolveCellWidget(col.type || 'text').component"
            v-bind="resolveCellWidget(col.type || 'text').props"
            :value="slotProps.data[col.field]"
            :row-data="slotProps.data"
            :column-config="col"
            @action="handleCellAction"
          />
        </template>
      </Column>
      
      <!-- Actions Column (if specified and not minimal) -->
      <Column v-if="config.actions && !minimal" header="Actions" :exportable="false" style="min-width:8rem">
        <template #body="slotProps">
          <ActionButtons 
            :actions="config.actions"
            :row-data="slotProps.data"
            @action="handleRowAction"
          />
        </template>
      </Column>
    </DataTable>
    
    <!-- Bulk Actions (hidden for minimal mode) -->
    <div v-if="config.bulkActions && selectedRows.length > 0 && !minimal" class="bulk-actions mt-3 p-3 surface-100 border-round">
      <BulkActions 
        :actions="config.bulkActions"
        :selected-count="selectedRows.length"
        @action="handleBulkAction"
      />
    </div>
  </div>
</template>

<script>
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import DisplayWidgetManager from '@/widgets/DisplayWidgetManager.js'
import SearchFilter from '@/components/filters/SearchFilter.vue'
import DateRangeFilter from '@/components/filters/DateRangeFilter.vue'
import ActionButtons from '@/components/actions/ActionButtons.vue'
import BulkActions from '@/components/actions/BulkActions.vue'

export default {
  name: 'DynamicTable',
  components: { 
    DataTable, 
    Column, 
    SearchFilter, 
    DateRangeFilter, 
    ActionButtons, 
    BulkActions 
  },
  
  props: {
    config: {
      type: Object,
      required: true
    },
    data: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    layout: {
      type: String,
      default: 'vertical',
      validator: value => ['vertical', 'horizontal'].includes(value)
    },
    compact: {
      type: Boolean,
      default: false
    },
    dense: {
      type: Boolean,
      default: false
    },
    minimal: {
      type: Boolean,
      default: false
    },
    responsive: {
      type: Boolean,
      default: false
    },
    breakpoints: {
      type: Object,
      default: () => ({
        xs: 0, sm: 576, md: 768, lg: 992, xl: 1200
      })
    }
  },
  
  computed: {
    tableClasses() {
      return {
        'compact': this.compact,
        'dense': this.dense,
        'minimal': this.minimal,
        [`layout-${this.layout}`]: true
      }
    },
    
    tableDataClasses() {
      return {
        'table-compact': this.compact,
        'table-dense': this.dense,
        'table-minimal': this.minimal
      }
    },
    
    visibleColumns() {
      if (!this.responsive) return this.config.columns
      
      return this.config.columns.filter(col => this.shouldShowColumn(col))
    }
  },
  
  data() {
    return {
      tableManager: new TableCellWidgetManager(),
      searchQuery: '',
      dateRange: null,
      selectedRows: [],
      filteredData: [...this.data],
      currentBreakpoint: 'lg',
      windowWidth: window.innerWidth
    }
  },
  
  mounted() {
    if (this.responsive) {
      window.addEventListener('resize', this.handleResize)
      this.updateBreakpoint()
    }
  },
  
  beforeUnmount() {
    if (this.responsive) {
      window.removeEventListener('resize', this.handleResize)
    }
  },
  
  methods: {
    // Resolve cell widget using TableCellWidgetManager
    resolveCellWidget(type) {
      return this.tableManager.getWidget(type, {}, null)
    },
    
    // Responsive breakpoint handling
    updateBreakpoint() {
      const width = this.windowWidth
      if (width >= this.breakpoints.xl) this.currentBreakpoint = 'xl'
      else if (width >= this.breakpoints.lg) this.currentBreakpoint = 'lg'
      else if (width >= this.breakpoints.md) this.currentBreakpoint = 'md'
      else if (width >= this.breakpoints.sm) this.currentBreakpoint = 'sm'
      else this.currentBreakpoint = 'xs'
    },
    
    handleResize() {
      this.windowWidth = window.innerWidth
      this.updateBreakpoint()
    },
    
    shouldShowColumn(column) {
      if (!this.responsive || !column.responsive) return true
      
      const { hide = [], show = [] } = column.responsive
      
      if (hide.includes(this.currentBreakpoint)) return false
      if (show.length > 0 && !show.includes(this.currentBreakpoint)) return false
      
      return true
    },
    
    // Handle search
    handleSearch(query) {
      this.searchQuery = query
      this.applyFilters()
    },
    
    // Handle date filter
    handleDateFilter(range) {
      this.dateRange = range
      this.applyFilters()
    },
    
    // Apply all filters
    applyFilters() {
      let filtered = [...this.data]
      
      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(item => 
          Object.values(item).some(value => 
            String(value).toLowerCase().includes(query)
          )
        )
      }
      
      // Date range filter
      if (this.dateRange && this.dateRange.start && this.dateRange.end) {
        filtered = filtered.filter(item => {
          const itemDate = new Date(item.created_at || item.updated_at)
          return itemDate >= this.dateRange.start && itemDate <= this.dateRange.end
        })
      }
      
      this.filteredData = filtered
    },
    
    // Handle row selection
    handleRowSelect(event) {
      this.$emit('row-select', event)
    },
    
    handleRowUnselect(event) {
      this.$emit('row-unselect', event)
    },
    
    // Handle row actions
    handleRowAction(action, rowData) {
      this.$emit('row-action', { action, rowData })
    },
    
    // Handle cell actions
    handleCellAction(action, rowData, columnConfig) {
      this.$emit('cell-action', { action, rowData, columnConfig })
    },
    
    // Handle bulk actions
    handleBulkAction(action) {
      this.$emit('bulk-action', { action, selectedRows: this.selectedRows })
    }
  },
  
  // Watch for data changes
  watch: {
    data: {
      handler(newData) {
        this.filteredData = [...newData]
        this.applyFilters()
      },
      deep: true
    }
  }
}
</script>

<style scoped>
/* Use PrimeFlex/PrimeVue utilities; avoid custom CSS here. */
.dynamic-table { width: 100%; }
</style>

## 📋 **LAYOUT CONFIGURATION:**

### **1. Vertical Layout (Default - for CRUD tables):**
```vue
<DynamicTable
  :config="artistTableConfig"
  layout="vertical"
  :compact="false"
  :dense="false"
  :minimal="false"
  @row-action="handleRowAction"
/>
```

### Server-side pagination/sorting/filtering/search (aligns with backend)
- Params mapping (DataTable → backend):
  - page: computed as `first/rows + 1`
  - per_page: bound to `rows`
  - sort: `sortField`, order: `asc|desc` from `sortOrder` (1|-1)
  - filters: convert to `filter_<field>=<op>:<value>` using backend ops (eq, ne, gt, lt, like, in)
- Responses:
  - Paginated: `{ data: [...], pagination: { page, per_page, total, pages } }`
  - Non-paginated: `{ data: [...], total }`
- Search endpoint:
  - GET `/api/{entity}/search` with `q`, optional `fields`, plus `page`, `per_page`, `sort`, `order`

### **2. Horizontal Layout (for dashboards, widgets):**
```vue
<DynamicTable
  :config="dashboardTableConfig"
  layout="horizontal"
  :compact="true"
  :dense="true"
  :minimal="true"
  @row-action="handleRowAction"
/>
```

### **3. Compact Mode (for inline tables, filters):**
```vue
<DynamicTable
  :config="inlineTableConfig"
  layout="vertical"
  :compact="true"
  :dense="true"
  :minimal="true"
  @row-action="handleRowAction"
/>
```

## 📋 **RESPONSIVE COLUMN CONFIGURATION:**

### **Artist Table with Responsive Columns:**
```javascript
// crud-configs/artist.js
export const artistCrudConfig = {
  entity: 'artist',
  table: {
    columns: [
      { 
        field: 'name', 
        header: 'Artist Name', 
        sortable: true,
        type: 'text',
        responsive: {
          hide: ['xs'],              // Hide on extra small screens
          show: ['sm', 'md', 'lg', 'xl']
        },
        props: {
          truncate: true,
          maxLength: 30
        }
      },
      { 
        field: 'abbreviation', 
        header: 'Abbr', 
        sortable: true,
        type: 'text',
        responsive: {
          hide: ['xs', 'sm'],        // Hide on small screens
          show: ['md', 'lg', 'xl']
        },
        props: {
          class: 'font-mono text-sm'
        }
      },
      { 
        field: 'albums_count', 
        header: 'Albums', 
        sortable: true,
        type: 'number',
        responsive: {
          hide: ['xs', 'sm', 'md'],  // Hide on small/medium screens
          show: ['lg', 'xl']
        },
        props: {
          format: '0,0'
        }
      },
      { 
        field: 'created_at', 
        header: 'Created', 
        sortable: true,
        type: 'date',
        responsive: {
          hide: ['xs', 'sm'],        // Hide on small screens
          show: ['md', 'lg', 'xl']
        },
        props: {
          format: 'MMM DD, YYYY'
        }
      },
      { 
        field: 'status', 
        header: 'Status', 
        sortable: true,
        type: 'status',
        responsive: {
          hide: [],                  // Always visible
          show: ['xs', 'sm', 'md', 'lg', 'xl']
        },
        props: {
          severity: 'info'
        }
      }
    ],
    actions: ['view', 'edit', 'delete'],
    bulkActions: ['delete', 'export'],
    filters: ['search', 'date_range'],
    sortable: true,
    paginated: true,
    pageSize: 20,
    selectionMode: 'multiple',
    resizable: true,
    striped: true,
    hover: true
  }
}
```

## 📁 **USAGE EXAMPLES:**

### **1. CRUD Table (Vertical, Full Features):**
```vue
<template>
  <div class="artists-view">
    <div class="view-header">
      <h1>Artists</h1>
      <Button @click="showCreateForm = true" icon="pi pi-plus">
        Add Artist
      </Button>
    </div>
    
    <DynamicTable
      :config="artistCrudConfig.table"
      :data="artists"
      :loading="loading"
      layout="vertical"
      :compact="false"
      :dense="false"
      :minimal="false"
      :responsive="true"
      @row-action="handleRowAction"
      @bulk-action="handleBulkAction"
    />
  </div>
</template>
```

### **2. Dashboard Widget (Horizontal, Compact, Minimal):**
```vue
<template>
  <div class="dashboard-widget">
    <h3>Recent Artists</h3>
    
    <DynamicTable
      :config="dashboardTableConfig"
      :data="recentArtists"
      layout="horizontal"
      :compact="true"
      :dense="true"
      :minimal="true"
      :responsive="true"
      @row-action="handleRowAction"
    />
  </div>
</template>
```

### **3. Inline Table (Compact, Dense, Minimal):**
```vue
<template>
  <div class="inline-section">
    <h4>Related Albums</h4>
    
    <DynamicTable
      :config="inlineTableConfig"
      :data="relatedAlbums"
      layout="vertical"
      :compact="true"
      :dense="true"
      :minimal="true"
      :responsive="true"
      @row-action="handleRowAction"
    />
  </div>
</template>
```

## 🎯 **KEY FEATURES:**

### **✅ Flexible Layouts:**
- **Vertical layout** - traditional table layout (default)
- **Horizontal layout** - compact horizontal layout for dashboards
- **Compact mode** - smaller fonts, tighter spacing
- **Dense mode** - tighter row heights
- **Minimal mode** - hide pagination, filters, bulk actions

### **✅ Responsive Support:**
- **Column hiding** - hide columns based on screen size
- **Breakpoint system** - customizable breakpoints (xs, sm, md, lg, xl)
- **Mobile-friendly** - automatically adapt to screen size
- **Progressive enhancement** - more features on larger screens

### **✅ Universal Usage:**
- **CRUD tables** - vertical, full features, responsive
- **Dashboard widgets** - horizontal, compact, minimal
- **Inline tables** - compact, dense, minimal
- **Filter results** - compact, dense, responsive

### **✅ Simple Configuration:**
- **`layout="horizontal"`** - horizontal layout
- **`:compact="true"`** - tight spacing
- **`:dense="true"`** - tight rows
- **`:minimal="true"`** - hide features
- **`:responsive="true"`** - enable responsive behavior

### **✅ Widget Manager Integration:**
- **TableCellWidgetManager** - handles all table cell widgets
- **Same input widgets** - work in any layout
- **Consistent behavior** - same rendering, same events
- **Reusable system** - one component, many use cases

**This gives you ONE table component that handles ALL table scenarios - just change the layout props!** 