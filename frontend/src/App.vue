<template>
  <div class="app-shell">
    <AppHeader v-if="showHeader" />
    <main class="app-content">
      <div class="content-container">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import AppHeader from "./components/AppHeader.vue";

const route = useRoute();
const showHeader = computed(() => route.name !== "login");
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  padding: 1rem 0 1.25rem;
}

.content-container {
  width: min(100%, 1120px);
  margin: 0 auto;
  padding: 0 0.85rem;
}

@media (min-width: 768px) {
  .app-content {
    padding: 1.25rem 0 1.5rem;
  }

  .content-container {
    padding: 0 1rem;
  }
}
</style>
