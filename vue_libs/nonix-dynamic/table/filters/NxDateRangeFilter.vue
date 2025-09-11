<template>
  <div class="date-range-filter flex align-items-center">
    <Calendar 
      v-model="dateRange"
      selectionMode="range"
      :showIcon="true"
      placeholder="Select date range"
      @date-select="handleDateSelect"
      class="w-12rem"
    />
  </div>
</template>

<script>
import Calendar from 'primevue/calendar'

export default {
  name: 'DateRangeFilter',
  components: { Calendar },
  
  props: {
    modelValue: {
      type: Object,
      default: () => null
    }
  },
  
  data() {
    return {
      dateRange: this.modelValue
    }
  },
  
  watch: {
    modelValue(newValue) {
      this.dateRange = newValue
    }
  },
  
  methods: {
    handleDateSelect() {
      this.$emit('update:modelValue', this.dateRange)
      this.$emit('change', this.dateRange)
    }
  }
}
</script>

<style scoped>
/* Using PrimeFlex utilities for layout/width. */
</style>
