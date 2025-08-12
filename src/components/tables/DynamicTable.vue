<template>
  <div class="dynamic-table" :class="tableClasses">
    <!-- Search and Filters -->
    <div v-if="config.filters && !minimal" class="table-filters">
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
    <div v-if="config.bulkActions && selectedRows.length > 0 && !minimal" class="bulk-actions">
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
import TableCellWidgetManager from '@/components/tables/TableCellWidgetManager.js'
import SearchFilter from '../filters/SearchFilter.vue'
import DateRangeFilter from '../filters/DateRangeFilter.vue'
import ActionButtons from '../actions/ActionButtons.vue'
import BulkActions from '../actions/BulkActions.vue'

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
.dynamic-table {
  width: 100%;
}

/* Vertical Layout (default) */
.layout-vertical .p-datatable {
  /* Normal table layout */
}

/* Horizontal Layout */
.layout-horizontal .p-datatable {
  /* Compact horizontal layout for dashboards */
}

/* Compact Mode */
.compact .p-datatable {
  font-size: 0.875rem;
}

.compact .p-datatable .p-datatable-thead > tr > th {
  padding: 0.5rem;
}

.compact .p-datatable .p-datatable-tbody > tr > td {
  padding: 0.5rem;
}

/* Dense Mode */
.dense .p-datatable .p-datatable-tbody > tr {
  height: 2.5rem;
}

.dense .p-datatable .p-datatable-thead > tr {
  height: 2.5rem;
}

/* Minimal Mode */
.minimal .p-paginator,
.minimal .p-datatable-header {
  display: none;
}

.minimal .p-datatable .p-datatable-thead > tr > th {
  border-bottom: 1px solid #e5e7eb;
}

/* Table Filters */
.table-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: center;
}

/* Bulk Actions */
.bulk-actions {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8fafc;
  border-radius: 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .compact .p-datatable .p-datatable-thead > tr > th,
  .compact .p-datatable .p-datatable-tbody > tr > td {
    padding: 0.25rem;
  }
}
</style>
