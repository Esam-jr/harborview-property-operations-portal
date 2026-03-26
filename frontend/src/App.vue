<template>
  <div class="app-shell">
    <AppHeader v-if="showHeader" />
    <main class="app-content">
      <router-view />
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
  padding: 1.5rem;
}
</style>
