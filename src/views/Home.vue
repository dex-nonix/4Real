<template>
  <Page
    title="Home"
    :back="false"
    :actions="[]"
    :showRightToggle="true"
  >
    <section class="p-3">
      <h1 class="m-0 mb-2">Hello World (Home)</h1>
      <p>This page uses the new Master shell + Page header mechanism.</p>
      <Button label="PrimeVue Button" icon="pi pi-check" />

      <div style="margin-top: 2rem;">
        <h2>Examples</h2>
        <p>Check out the DynamicForm and DynamicTable components in action:</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
          <router-link to="/dynamic-form" class="example-link">
            <Button label="DynamicForm Example" icon="pi pi-file-edit" severity="secondary" />
          </router-link>
          <router-link to="/dynamic-table" class="example-link">
            <Button label="DynamicTable Example" icon="pi pi-table" severity="secondary" />
          </router-link>
        </div>
      </div>

      <div class="grid" style="margin-top: 2rem;">
        <div class="col-12 md:col-6">
          <h3 class="m-0 mb-2">Chat Component A</h3>
          <Chat />
        </div>
        <div class="col-12 md:col-6">
          <h3 class="m-0 mb-2">Chat Component B</h3>
          <Chat />
        </div>
      </div>
    </section>
  </Page>
</template>

<script setup>
import Button from 'primevue/button'
import Page from '@nonix/page/Page.vue'
import Chat from '@nonix-chat/components/Chat.vue'
</script>

<style scoped>
.example-link {
  text-decoration: none;
}
</style>

