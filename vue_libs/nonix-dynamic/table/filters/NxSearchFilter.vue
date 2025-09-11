<template>
  <div class="search-filter flex align-items-center">
    <InputText
        v-model="searchValue"
        :placeholder="placeholder"
        @input="handleInput"
        class="w-12rem"
    />
  </div>
</template>

<script>
import InputText from 'primevue/inputtext'

export default {
  name: 'NxSearchFilter',
  components: {InputText},

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
/* Using PrimeFlex utilities for layout/width. */
</style>
