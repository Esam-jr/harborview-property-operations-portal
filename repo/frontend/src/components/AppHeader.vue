<template>
  <header class="header">
    <div class="brand-row">
      <h1>HarborView Portal</h1>
      <div class="brand-actions">
        <span class="user-chip">{{ auth.state.username }} ({{ auth.state.role || "unknown" }})</span>
        <button type="button" class="menu-btn" @click="menuOpen = !menuOpen">
          {{ menuOpen ? "Close Menu" : "Menu" }}
        </button>
      </div>
    </div>

    <nav :class="{ 'is-open': menuOpen }">
      <router-link to="/home" @click="menuOpen = false">Home</router-link>
      <router-link to="/dashboard" @click="menuOpen = false">Dashboard</router-link>
      <router-link
        v-if="auth.state.role === 'resident'"
        to="/resident-dashboard"
        @click="menuOpen = false"
      >
        Resident Dashboard
      </router-link>
      <router-link v-if="auth.state.role === 'manager'" to="/listings" @click="menuOpen = false">
        Listings
      </router-link>
      <router-link to="/service-orders" @click="menuOpen = false">Service Orders</router-link>
      <router-link to="/billing" @click="menuOpen = false">Billing</router-link>

      <div v-if="pwaState.enabled" class="install-action">
        <span class="install-pill">{{ pwaState.online ? "Online" : "Offline" }}</span>
        <button
          v-if="pwaState.installable"
          type="button"
          class="install-button"
          @click="handleInstall"
        >
          Install App
        </button>
      </div>

      <button class="link-btn" @click="logout">Logout</button>
    </nav>
  </header>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";
import { installOfflineApp, pwaState } from "../services/pwaService";

const router = useRouter();
const auth = useAuthStore();
const menuOpen = ref(false);

async function handleInstall() {
  await installOfflineApp();
}

function logout() {
  auth.clearAuth();
  menuOpen.value = false;
  router.push({ name: "login" });
}
</script>

<style scoped>
.header {
  padding: 0.85rem 1rem;
  background: #0f172a;
  color: #e2e8f0;
  display: grid;
  gap: 0.7rem;
}

.brand-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.brand-row h1 {
  margin: 0;
  font-size: 1.1rem;
}

.brand-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.menu-btn {
  display: inline-flex;
  border: 1px solid #334155;
  background: #1e293b;
  color: #e2e8f0;
}

.user-chip {
  padding: 0.25rem 0.5rem;
  border: 1px solid #334155;
  border-radius: 6px;
  font-size: 0.85rem;
}

nav {
  display: none;
  gap: 0.9rem;
  align-items: center;
  flex-wrap: wrap;
}

nav.is-open {
  display: flex;
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

@media (min-width: 900px) {
  .header {
    padding: 1rem 1.5rem;
  }

  .brand-row h1 {
    font-size: 1.25rem;
  }

  .menu-btn {
    display: none;
  }

  nav {
    display: flex;
  }
}

@media (max-width: 560px) {
  .user-chip {
    display: none;
  }
}
</style>
