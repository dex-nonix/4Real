<template>
  <section>
    <h1>DynamicTable Example</h1>
    <p>This page demonstrates the DynamicTable component with the widget manager system.</p>
    
    <!-- CRUD Table Example -->
    <div class="example-section">
      <h2>Artists CRUD Table (Vertical, Full Features)</h2>
      <DynamicTable 
        :config="artistCrudConfig"
        :data="artists"
        :loading="loading"
        layout="vertical"
        :compact="false"
        :dense="false"
        :minimal="false"
        :responsive="true"
        @row-action="handleRowAction"
        @bulk-action="handleBulkAction"
        @row-select="handleRowSelect"
      />
    </div>

    <!-- Dashboard Widget Example -->
    <div class="example-section">
      <h2>Recent Artists Dashboard (Horizontal, Compact, Minimal)</h2>
      <DynamicTable 
        :config="dashboardConfig"
        :data="recentArtists"
        layout="horizontal"
        :compact="true"
        :dense="true"
        :minimal="true"
        :responsive="true"
        @row-action="handleRowAction"
      />
    </div>

    <!-- Inline Table Example -->
    <div class="example-section">
      <h2>Related Albums Inline (Compact, Dense, Minimal)</h2>
      <DynamicTable 
        :config="inlineConfig"
        :data="relatedAlbums"
        layout="vertical"
        :compact="true"
        :dense="true"
        :minimal="true"
        :responsive="true"
        @row-action="handleRowAction"
      />
    </div>

    <!-- Icons Only Example -->
    <div class="example-section">
      <h2>Icons Only Actions (Compact, Minimal)</h2>
      <DynamicTable 
        :config="iconsOnlyConfig"
        :data="iconsOnlyData"
        layout="vertical"
        :compact="true"
        :dense="true"
        :minimal="true"
        :responsive="true"
        @row-action="handleRowAction"
      />
    </div>

    <!-- Text Only Example -->
    <div class="example-section">
      <h2>Text Only Actions (Compact, Minimal)</h2>
      <DynamicTable 
        :config="textOnlyConfig"
        :data="textOnlyData"
        layout="vertical"
        :compact="true"
        :dense="true"
        :minimal="true"
        :responsive="true"
        @row-action="handleRowAction"
      />
    </div>

    <!-- Both Icons and Text Example -->
    <div class="example-section">
      <h2>Both Icons and Text Actions (Compact, Minimal)</h2>
      <DynamicTable 
        :config="bothConfig"
        :data="bothData"
        layout="vertical"
        :compact="true"
        :dense="true"
        :minimal="true"
        :responsive="true"
        @row-action="handleRowAction"
      />
    </div>

    <!-- Table Data Display -->
    <div class="example-section">
      <h3>Current Table Data:</h3>
      <pre>{{ JSON.stringify({ artists: artists.length, recentArtists: recentArtists.length, relatedAlbums: relatedAlbums.length }, null, 2) }}</pre>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import DynamicTable from '@/libs/core/dynamic-table/DynamicTable.vue'

// Loading state
const loading = ref(false)

// Sample data
const artists = ref([
  {
    id: 1,
    name: 'TRC',
    abbreviation: 'TRC',
    status: 'active',
    albums_count: 3,
    created_at: '2023-01-15',
    image: 'https://via.placeholder.com/40'
  },
  {
    id: 2,
    name: 'Underground King',
    abbreviation: 'UGK',
    status: 'active',
    albums_count: 2,
    created_at: '2023-02-20',
    image: 'https://via.placeholder.com/40'
  },
  {
    id: 3,
    name: 'Street Poet',
    abbreviation: 'SP',
    status: 'inactive',
    albums_count: 1,
    created_at: '2023-03-10',
    image: 'https://via.placeholder.com/40'
  }
])

const recentArtists = ref(artists.value.slice(0, 2))
const relatedAlbums = ref([
  { id: 1, title: 'Rise From Ashes', artist: 'TRC', year: 2023 },
  { id: 2, title: 'Di Streets Talk', artist: 'TRC', year: 2023 },
  { id: 3, title: 'No Mercy', artist: 'TRC', year: 2023 }
])

// Sample data for new examples
const iconsOnlyData = ref([
  { id: 1, name: 'Icon Item 1', type: 'Type A' },
  { id: 2, name: 'Icon Item 2', type: 'Type B' },
  { id: 3, name: 'Icon Item 3', type: 'Type C' }
])

const textOnlyData = ref([
  { id: 1, title: 'Text Item 1', category: 'Category A' },
  { id: 2, title: 'Text Item 2', category: 'Category B' },
  { id: 3, title: 'Text Item 3', category: 'Category C' }
])

const bothData = ref([
  { id: 1, name: 'Both Item 1', status: 'active' },
  { id: 2, name: 'Both Item 2', status: 'inactive' },
  { id: 3, name: 'Both Item 3', status: 'pending' }
])

// Artist CRUD table configuration
const artistCrudConfig = {
  columns: [
    { 
      field: 'name', 
      header: 'Artist Name', 
      sortable: true,
      type: 'text',
      responsive: {
        hide: ['xs'],
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
        hide: ['xs', 'sm'],
        show: ['md', 'lg', 'xl']
      },
      props: {
        class: 'font-mono text-sm'
      }
    },
    { 
      field: 'status', 
      header: 'Status', 
      sortable: true,
      type: 'status',
      responsive: {
        hide: [],
        show: ['xs', 'sm', 'md', 'lg', 'xl']
      },
      props: {
        severity: 'info'
      }
    },
    { 
      field: 'albums_count', 
      header: 'Albums', 
      sortable: true,
      type: 'number',
      responsive: {
        hide: ['xs', 'sm', 'md'],
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
        hide: ['xs', 'sm'],
        show: ['md', 'lg', 'xl']
      },
      props: {
        format: 'MMM DD, YYYY'
      }
    },
    { 
      field: 'image', 
      header: 'Image', 
      sortable: false,
      type: 'image',
      responsive: {
        hide: ['xs', 'sm'],
        show: ['md', 'lg', 'xl']
      }
    }
  ],
  actions: ['view', 'edit', 'delete'],
  bulkActions: ['delete', 'export'],
  filters: ['search', 'date_range'],
  sortable: true,
  paginated: true,
  pageSize: 10,
  selectionMode: 'multiple',
  resizable: true,
  striped: true,
  hover: true
}

// Dashboard table configuration
const dashboardConfig = {
  columns: [
    { field: 'name', header: 'Artist', type: 'text' },
    { field: 'status', header: 'Status', type: 'status' },
    { field: 'albums_count', header: 'Albums', type: 'number' }
  ],
  actions: ['view'],
  sortable: false,
  paginated: false,
  striped: false,
  hover: false
}

// Inline table configuration
const inlineConfig = {
  columns: [
    { field: 'title', header: 'Title', type: 'text' },
    { field: 'artist', header: 'Artist', type: 'text' },
    { field: 'year', header: 'Year', type: 'number' }
  ],
  actions: ['view', 'edit'],
  sortable: false,
  paginated: false,
  striped: false,
  hover: false
}

// Icons only example
const iconsOnlyConfig = {
  columns: [
    { field: 'name', header: 'Name', type: 'text' },
    { field: 'type', header: 'Type', type: 'text' }
  ],
  actions: ['view', 'edit', 'delete'],
  actionsDisplay: 'icons-only',
  sortable: false,
  paginated: false,
  striped: false,
  hover: false
}

// Text only example
const textOnlyConfig = {
  columns: [
    { field: 'title', header: 'Title', type: 'text' },
    { field: 'category', header: 'Category', type: 'text' }
  ],
  actions: ['view', 'edit', 'delete'],
  actionsDisplay: 'text-only',
  sortable: false,
  paginated: false,
  striped: false,
  hover: false
}

// Both icons and text example
const bothConfig = {
  columns: [
    { field: 'name', header: 'Name', type: 'text' },
    { field: 'status', header: 'Status', type: 'status' }
  ],
  actions: ['view', 'edit', 'delete'],
  actionsDisplay: 'both',
  sortable: false,
  paginated: false,
  striped: false,
  hover: false
}

// Event handlers
const handleRowAction = ({ action, rowData }) => {
  console.log('Row action:', action, rowData)
  alert(`${action} action for ${rowData.name || rowData.title}`)
}

const handleBulkAction = ({ action, selectedRows }) => {
  console.log('Bulk action:', action, selectedRows)
  alert(`${action} action for ${selectedRows.length} selected items`)
}

const handleRowSelect = (event) => {
  console.log('Row selected:', event)
}
</script>

<style scoped>
.example-section {
  margin: 2rem 0;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.example-section h2 {
  margin-top: 0;
  color: #374151;
}

.example-section h3 {
  color: #6b7280;
}

pre {
  background-color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  font-size: 0.875rem;
}
</style>
