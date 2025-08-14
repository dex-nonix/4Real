<template>
  <section>
    <h1>DynamicForm Example</h1>
    <p>This page demonstrates the DynamicForm component with the widget manager system.</p>
    
    <!-- Example Form Configuration -->
    <div class="example-section">
      <h2>Artist Form Example</h2>
      <DynamicForm 
        :config="artistFormConfig"
        :initial-data="artistData"
        submit-label="Save Artist"
        @submit="handleSubmit"
        @field-change="handleFieldChange"
      />
    </div>

    <!-- Form Data Display -->
    <div class="example-section">
      <h3>Current Form Data:</h3>
      <pre>{{ JSON.stringify(formData, null, 2) }}</pre>
    </div>

    <!-- Filter Form Example -->
    <div class="example-section">
      <h2>Artist Filter Example</h2>
      <DynamicForm 
        :config="filterConfig"
        layout="horizontal"
        :compact="true"
        @field-change="handleFilterChange"
      />
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import DynamicForm from '@nonix/dynamic-form/DynamicForm.vue'

// Form data
const formData = ref({
  name: '',
  abbreviation: '',
  persona: '',
  status: 'active'
})

// Artist form configuration (array-based)
const artistFormConfig = {
  fields: [
    {
      key: 'name',
      type: 'text',
      label: 'Artist Name',
      required: true,
      props: { 
        placeholder: 'Enter artist name',
        class: 'w-full'
      }
    },
    {
      key: 'abbreviation',
      type: 'text',
      label: 'Abbreviation',
      required: true,
      props: { 
        placeholder: 'Enter abbreviation',
        class: 'w-full'
      }
    },
    {
      key: 'status',
      type: 'select',
      label: 'Status',
      required: true,
      props: { 
        options: [
          { label: 'Active', value: 'active' },
          { label: 'Inactive', value: 'inactive' },
          { label: 'Pending', value: 'pending' }
        ],
        placeholder: 'Select status',
        class: 'w-full'
      },
      check: (formData) => {
        if (formData.status === 'active') {
          return [
            { key: 'advancedOption', type: 'text', label: 'Advanced Option' },
            { key: 'tuning', type: 'slider', label: 'Tuning' }
          ]
        }
        return true
      }
    },
    {
      key: 'persona',
      type: 'json',
      label: 'Artist Persona',
      props: { 
        height: '200px',
        class: 'w-full'
      }
    },
    {
      // dataless UI-only example item
      type: 'text',
      label: 'Advanced options visible when status is Active',
      check: (formData, i, item) => (formData.status === 'active' ? item : null)
    }
  ]
}

// Filter configuration (array-based)
const filterConfig = {
  fields: [
    {
      key: 'search',
      type: 'text',
      label: 'Search',
      props: { 
        placeholder: 'Search artists...',
        class: 'w-64'
      }
    },
    {
      key: 'status',
      type: 'select',
      label: 'Status',
      props: { 
        options: [
          { label: 'All', value: '' },
          { label: 'Active', value: 'active' },
          { label: 'Inactive', value: 'inactive' }
        ],
        placeholder: 'All statuses',
        class: 'w-32'
      }
    }
  ]
}

// Initial artist data
const artistData = ref({
  name: 'TRC',
  abbreviation: 'TRC',
  status: 'active',
  persona: 'Underground artist from the streets'
})

// Event handlers
const handleSubmit = (data) => {
  console.log('Form submitted:', data)
  formData.value = { ...data }
  alert('Artist saved successfully!')
}

const handleFieldChange = ({ key, value, formData: currentFormData }) => {
  console.log('Field changed:', key, value)
  formData.value = { ...currentFormData }
}

const handleFilterChange = ({ key, value }) => {
  console.log('Filter changed:', key, value)
  // Apply filters to data
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
