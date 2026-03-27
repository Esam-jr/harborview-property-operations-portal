<template>
  <header class="header">
    <div class="brand-row">
      <h1>HarborView Portal</h1>
      <span class="user-chip">{{ auth.state.username }} ({{ auth.state.role || "unknown" }})</span>
    </div>
    <nav>
      <router-link to="/home">Home</router-link>
      <router-link to="/dashboard">Dashboard</router-link>
      <router-link v-if="auth.state.role === 'resident'" to="/resident-dashboard">Resident Dashboard</router-link>
      <router-link v-if="auth.state.role === 'manager'" to="/listings">Listings</router-link>
      <router-link to="/service-orders">Service Orders</router-link>
      <router-link to="/billing">Billing</router-link>
      <button class="link-btn" @click="logout">Logout</button>
    </nav>
  </header>
</template>

<script setup>
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

function logout() {
  auth.clearAuth();
  router.push({ name: "login" });
}
</script>

<style scoped>
.header {
  padding: 1rem 1.5rem;
  background: #0f172a;
  color: #e2e8f0;
  display: grid;
  gap: 0.75rem;
}

.brand-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.user-chip {
  padding: 0.25rem 0.5rem;
  border: 1px solid #334155;
  border-radius: 6px;
  font-size: 0.85rem;
}

nav {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

a,
.link-btn {
  text-decoration: none;
  color: #e2e8f0;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font: inherit;
}

a.router-link-active {
  color: #38bdf8;
}
</style>
