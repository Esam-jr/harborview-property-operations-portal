<template>
  <div class="app-shell">
    <AppHeader />
    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import AppHeader from "./components/AppHeader.vue";
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  padding: 1.5rem;
}
</style>
