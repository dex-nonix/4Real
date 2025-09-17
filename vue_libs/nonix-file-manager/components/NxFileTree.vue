<template>
  <div class="file-tree">
    <div class="tree-header">
      <h6>Categories</h6>
      <Button
        v-if="allowCreateCategory"
        icon="pi pi-plus"
        size="small"
        @click="showCreateDialog = true"
        v-tooltip="'Create Category'"
      />
    </div>

    <!-- Flat Categories View (initial implementation) -->
    <div v-if="!hierarchical" class="flat-categories">
      <div
        v-for="category in categories"
        :key="category.id"
        :class="['category-item', { 'selected': selectedCategories.includes(category.id) }]"
        @click="toggleCategory(category.id)"
      >
        <i :class="getCategoryIcon(category)" class="mr-2"></i>
        <span>{{ category.name }}</span>
        <small v-if="showCounts" class="ml-auto text-muted">
          {{ fileCounts[category.id] || 0 }}
        </small>
      </div>
    </div>

    <!-- Hierarchical Tree View (future implementation) -->
    <Tree
      v-else
      :value="treeData"
      :selectionMode="selectionMode"
      v-model:selectionKeys="selectedKeys"
      @selection-change="handleTreeSelectionChange"
    >
      <template #default="slotProps">
        <span class="tree-node">
          <i :class="getCategoryIcon(slotProps.node)" class="mr-2"></i>
          {{ slotProps.node.label }}
          <small v-if="showCounts" class="ml-auto text-muted">
            {{ slotProps.node.fileCount || 0 }}
          </small>
        </span>
      </template>
    </Tree>

    <!-- Create Category Dialog -->
    <Dialog
      v-model:visible="showCreateDialog"
      modal
      header="Create Category"
      :style="{ width: '400px' }"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="categoryName">Category Name</label>
          <InputText
            id="categoryName"
            v-model="newCategoryName"
            @keyup.enter="createCategory"
          />
        </div>
      </div>
      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="showCreateDialog = false"
        />
        <Button
          label="Create"
          icon="pi pi-check"
          :loading="creating"
          @click="createCategory"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject, defineProps, defineEmits } from 'vue'
import Tree from 'primevue/tree'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'

// Props
const props = defineProps({
  categories: {
    type: Array,
    required: true
  },
  selectedCategories: {
    type: Array,
    default: () => []
  },
  selectionMode: {
    type: String,
    default: 'single',
    validator: value => ['single', 'multiple'].includes(value)
  },
  hierarchical: {
    type: Boolean,
    default: false // Start with flat categories, set to true when parent_id is implemented
  },
  showCounts: {
    type: Boolean,
    default: true // Show file count per category
  },
  treeData: {
    type: Array,
    default: () => [] // For hierarchical tree structure (future use)
  },
  allowCreateCategory: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['category-select', 'category-unselect', 'selection-change', 'category-created', 'update:selectedCategories'])

// Services
const fileOperationsService = inject('fileOperations')

// Reactive state
const selectedKeys = ref({})
const showCreateDialog = ref(false)
const newCategoryName = ref('')
const creating = ref(false)
const fileCounts = ref({}) // Cache for file counts

// Methods
const toggleCategory = (categoryId) => {
  if (props.selectionMode === 'single') {
    // For single selection, just select this category (replace current selection)
    if (props.selectedCategories[0] !== categoryId) {
      const oldCategory = props.selectedCategories[0]
      if (oldCategory) {
        emit('category-unselect', oldCategory)
      }
      emit('category-select', categoryId)
      emit('update:selectedCategories', [categoryId])
    }
  } else {
    // For multiple selection, toggle the category
    const isSelected = props.selectedCategories.includes(categoryId)
    let newSelectedCategories

    if (isSelected) {
      // Remove category
      newSelectedCategories = props.selectedCategories.filter(id => id !== categoryId)
      emit('category-unselect', categoryId)
    } else {
      // Add category
      newSelectedCategories = [...props.selectedCategories, categoryId]
      emit('category-select', categoryId)
    }

    // Emit v-model update
    emit('update:selectedCategories', newSelectedCategories)
  }
}

const handleTreeSelectionChange = (event) => {
  // event contains the new selectionKeys object from PrimeVue Tree
  selectedKeys.value = event

  // Convert selectedKeys back to selectedCategories array
  const newSelectedCategories = Object.keys(selectedKeys.value).filter(key => selectedKeys.value[key])

  // For single selection, ensure only one category is selected
  if (props.selectionMode === 'single' && newSelectedCategories.length > 1) {
    // Keep only the last selected category
    const lastSelected = newSelectedCategories[newSelectedCategories.length - 1]
    selectedKeys.value = { [lastSelected]: true }
    newSelectedCategories.splice(0, newSelectedCategories.length - 1)
  }

  emit('update:selectedCategories', newSelectedCategories)
}

const getCategoryIcon = (category) => {
  // Simple icon logic - can be enhanced
  return 'pi pi-folder'
}

const loadFileCounts = async () => {
  if (!props.showCounts || !fileOperationsService) return

  for (const category of props.categories) {
    if (fileCounts.value[category.id] === undefined) {
      const count = await fileOperationsService.getCategoryFileCount(category.id)
      fileCounts.value[category.id] = count
    }
  }
}

const getCategoryFileCount = async (categoryId) => {
  if (fileCounts.value[categoryId] !== undefined) {
    return fileCounts.value[categoryId]
  }

  if (!fileOperationsService) {
    return 0
  }

  const count = await fileOperationsService.getCategoryFileCount(categoryId)
  fileCounts.value[categoryId] = count
  return count
}

const createCategory = async () => {
  if (!newCategoryName.value.trim()) return

  creating.value = true
  try {
    const result = await fileOperationsService.createCategory(newCategoryName.value.trim())
    if (result.success) {
      emit('category-created', result.result)
      showCreateDialog.value = false
      newCategoryName.value = ''
      // Refresh file counts cache
      fileCounts.value = {}
    }
  } catch (error) {
    console.error('Create category error:', error)
  } finally {
    creating.value = false
  }
}

// Watchers
watch(() => props.categories, () => {
  loadFileCounts()
}, { immediate: true })

watch(() => props.selectedCategories, (newVal) => {
  if (!props.hierarchical) return
  // Convert array to tree selection keys for hierarchical mode
  selectedKeys.value = {}
  newVal.forEach(id => {
    selectedKeys.value[id] = true
  })
}, { immediate: true })

// Lifecycle
onMounted(() => {
  loadFileCounts()
})
</script>

<style scoped>
.file-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid var(--surface-border);
}

.tree-header h6 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.flat-categories {
  flex: 1;
  overflow-y: auto;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.category-item:hover {
  background-color: var(--surface-hover);
}

.category-item.selected {
  background-color: var(--primary-100);
  color: var(--primary-700);
}

.category-item i {
  font-size: 1rem;
  color: var(--primary-500);
}

.category-item span {
  flex: 1;
  font-size: 0.875rem;
}

.category-item small {
  font-size: 0.75rem;
  opacity: 0.7;
}

.tree-node {
  display: flex;
  align-items: center;
  width: 100%;
}

.tree-node i {
  font-size: 1rem;
  color: var(--primary-500);
}

.tree-node span {
  flex: 1;
  font-size: 0.875rem;
}

.tree-node small {
  font-size: 0.75rem;
  opacity: 0.7;
}
</style>
