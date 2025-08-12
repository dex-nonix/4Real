<template>
  <div class="search-filter">
    <InputText 
      v-model="searchValue"
      :placeholder="placeholder"
      @input="handleInput"
      class="search-input"
    />
  </div>
</template>

<script>
import InputText from 'primevue/inputtext'

export default {
  name: 'SearchFilter',
  components: { InputText },
  
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Search...'
    }
  },
  
  data() {
    return {
      searchValue: this.modelValue
    }
  },
  
  watch: {
    modelValue(newValue) {
      this.searchValue = newValue
    }
  },
  
  methods: {
    handleInput() {
      this.$emit('update:modelValue', this.searchValue)
      this.$emit('search', this.searchValue)
    }
  }
}
</script>

<style scoped>
.search-filter {
  display: flex;
  align-items: center;
}

.search-input {
  min-width: 200px;
}
</style>
