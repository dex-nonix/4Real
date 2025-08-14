<template>
  <Page title="Chat" :back="false" :actions="[]" :showRightToggle="true">
    <section class="p-3">
      <ChatWidget instance-id="main" />
    </section>
  </Page>
</template>

<script setup>
import Page from '@nonix/page/Page.vue'
import ChatWidget from '@nonix-chat/ChatWidget.vue'
</script>


