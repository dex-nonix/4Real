# 📊 DynamicTable Component

## 🎯 **PURPOSE:**
**Generic table component that uses the widget manager system to render any data table with custom cell widgets**

## 🏗️ **ARCHITECTURE:**

### **Core Concept:**
- **Configuration-driven tables** - no hardcoded table layouts
- **Widget manager integration** - uses TableCellWidgetManager for cell rendering
- **Generic data handling** - works with any data structure
- **Custom cell widgets** - different rendering for different data types

## 🔧 **IMPLEMENTATION:**

### **1. DynamicTable.vue Component:**
```vue
<template>
  <div class="dynamic-table">
    <!-- Search and Filters -->
    <div v-if="config.filters" class="table-filters">
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
      :columns="config.columns"
      :paginator="config.paginated"
      :rows="config.pageSize || 10"
      :loading="loading"
      :sortable="config.sortable"
      :resizable-columns="config.resizable"
      :striped-rows="config.striped"
      :row-hover="config.hover"
      :selection-mode="config.selectionMode"
      v-model:selection="selectedRows"
      @row-select="handleRowSelect"
      @row-unselect="handleRowUnselect"
    >
      <!-- Dynamic Column Rendering -->
      <Column 
        v-for="col in config.columns" 
        :key="col.field" 
        :field="col.field" 
        :header="col.header"
        :sortable="col.sortable !== false"
        :filter="col.filter"
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
      
      <!-- Actions Column (if specified) -->
      <Column v-if="config.actions" header="Actions" :exportable="false" style="min-width:8rem">
        <template #body="slotProps">
          <ActionButtons 
            :actions="config.actions"
            :row-data="slotProps.data"
            @action="handleRowAction"
          />
        </template>
      </Column>
    </DataTable>
    
    <!-- Bulk Actions -->
    <div v-if="config.bulkActions && selectedRows.length > 0" class="bulk-actions">
      <BulkActions 
        :actions="config.bulkActions"
        :selected-count="selectedRows.length"
        @action="handleBulkAction"
      />
    </div>
  </div>
</template>

<script>
import { DataTable, Column } from 'primevue/datatable'
import { TableCellWidgetManager } from '@/widgets/TableCellWidgetManager.js'
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
    }
  },
  
  data() {
    return {
      tableManager: new TableCellWidgetManager(),
      searchQuery: '',
      dateRange: null,
      selectedRows: [],
      filteredData: [...this.data]
    }
  },
  
  methods: {
    // Resolve cell widget using TableCellWidgetManager
    resolveCellWidget(type) {
      return this.tableManager.getWidget(type, {}, null)
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
.dynamic-table {
  width: 100%;
}

.table-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: center;
}

.bulk-actions {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8fafc;
  border-radius: 0.5rem;
}
</style>

## 📋 **CRUD CONFIG INTEGRATION:**

### **Artist Table Configuration:**
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
        props: {
          class: 'font-mono text-sm'
        }
      },
      { 
        field: 'albums_count', 
        header: 'Albums', 
        sortable: true,
        type: 'number',
        props: {
          format: '0,0'
        }
      },
      { 
        field: 'created_at', 
        header: 'Created', 
        sortable: true,
        type: 'date',
        props: {
          format: 'MMM DD, YYYY'
        }
      },
      { 
        field: 'status', 
        header: 'Status', 
        sortable: true,
        type: 'status',
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

## 🔄 **CELL WIDGET TYPES:**

### **Text Cell Widget:**
```javascript
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

## 📁 **USAGE:**

### **In Artist Management View:**
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
      @row-action="handleRowAction"
      @bulk-action="handleBulkAction"
    />
  </div>
</template>

<script>
import DynamicTable from '@/components/core/DynamicTable.vue'
import { Button } from 'primevue/button'
import { artistCrudConfig } from '@/configs/crud/artist.js'

export default {
  components: { DynamicTable, Button },
  data() {
    return {
      artistCrudConfig,
      artists: [],
      loading: false,
      showCreateForm: false
    }
  },
  methods: {
    async handleRowAction({ action, rowData }) {
      switch (action) {
        case 'view':
          this.$router.push(`/artists/${rowData.id}`)
          break
        case 'edit':
          this.$router.push(`/artists/${rowData.id}/edit`)
          break
        case 'delete':
          await this.deleteArtist(rowData.id)
          break
      }
    },
    
    async handleBulkAction({ action, selectedRows }) {
      if (action === 'delete') {
        await this.bulkDeleteArtists(selectedRows.map(row => row.id))
      }
    }
  }
}
</script>
```

## 🎯 **KEY FEATURES:**

### **✅ Generic Table Building:**
- **Any data structure** - artists, albums, tracks, etc.
- **Dynamic column rendering** - based on widget manager
- **Custom cell widgets** - different rendering per data type

### **✅ Widget Manager Integration:**
- **TableCellWidgetManager** - handles all table cell widgets
- **Default props** - sensible defaults for each widget type
- **User props** - override defaults when needed

### **✅ PrimeVue Compatibility:**
- **DataTable component** - full PrimeVue table functionality
- **Custom cell rendering** - with any Vue component
- **Built-in features** - sorting, filtering, pagination, selection

### **✅ Advanced Features:**
- **Search and filtering** - global search, date ranges
- **Bulk operations** - multi-select actions
- **Row actions** - view, edit, delete per row
- **Responsive design** - resizable columns, mobile friendly

**This gives you a completely generic table system that works with any data and any cell widget type!** 