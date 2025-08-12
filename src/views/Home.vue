<template>
  <section>
    <h1>Hello World (Home)</h1>
    <p>This page uses the Master layout.</p>
    <Button label="PrimeVue Button" icon="pi pi-check" />
    
    <div style="margin-top: 2rem;">
      <h2>Examples</h2>
      <p>Check out the DynamicForm and DynamicTable components in action:</p>
      <div style="display: flex; gap: 1rem; margin-top: 1rem;">
        <router-link to="/dynamic-form" class="example-link">
          <Button label="DynamicForm Example" icon="pi pi-form" severity="secondary" />
        </router-link>
        <router-link to="/dynamic-table" class="example-link">
          <Button label="DynamicTable Example" icon="pi pi-table" severity="secondary" />
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import Button from 'primevue/button'
</script>

<style scoped>
.example-link {
  text-decoration: none;
}
</style>

