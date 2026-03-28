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
      <router-link v-if="canAccessResidentDashboard" to="/resident-dashboard" @click="menuOpen = false">
        Resident Dashboard
      </router-link>
      <router-link v-if="canAccessListings" to="/listings" @click="menuOpen = false">
        Listings
      </router-link>
      <router-link v-if="canAccessOrders" to="/service-orders" @click="menuOpen = false">Service Orders</router-link>
      <router-link v-if="canAccessBilling" to="/billing" @click="menuOpen = false">Billing</router-link>

      <div v-if="pwaState.enabled" class="install-action">
        <span class="install-pill">{{ pwaState.online ? "Online" : "Offline" }}</span>
        <button
          v-if="pwaState.installable"
          type="button"
          class="install-button"
          :class="{ 'is-loading': installLoading }"
          :disabled="installLoading"
          @click="handleInstall"
        >
          {{ installLoading ? "Installing..." : "Install App" }}
        </button>
      </div>

      <button class="link-btn" @click="logout">Logout</button>
    </nav>
  </header>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";
import { installOfflineApp, pwaState } from "../services/pwaService";

const router = useRouter();
const auth = useAuthStore();
const menuOpen = ref(false);
const installLoading = ref(false);

const canAccessResidentDashboard = computed(() => auth.state.role === "resident");
const canAccessListings = computed(() => auth.state.role === "manager");
const canAccessOrders = computed(() =>
  ["admin", "manager", "dispatcher", "resident"].includes(auth.state.role),
);
const canAccessBilling = computed(() =>
  ["admin", "manager", "clerk", "resident"].includes(auth.state.role),
);

async function handleInstall() {
  installLoading.value = true;
  try {
    await installOfflineApp();
  } finally {
    installLoading.value = false;
  }
}

function logout() {
  auth.clearAuth();
  menuOpen.value = false;
  router.push({ name: "login" });
}
</script>

<style scoped>
.header {
  padding: 0.9rem 1rem;
  background: #0f172a;
  color: #eaf2ff;
  display: grid;
  gap: 0.8rem;
  border-bottom: 1px solid #22344b;
}

.brand-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.brand-row h1 {
  margin: 0;
  font-size: 1.08rem;
  letter-spacing: 0.01em;
}

.brand-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.menu-btn {
  display: inline-flex;
  border: 1px solid #3a516d;
  background: #1f334a;
  color: #eaf2ff;
}

.user-chip {
  padding: 0.28rem 0.56rem;
  border: 1px solid #3a516d;
  border-radius: 8px;
  font-size: 0.85rem;
  background: #1b2d42;
}

nav {
  display: none;
  gap: 0.8rem;
  align-items: center;
  flex-wrap: wrap;
}

nav.is-open {
  display: flex;
}

a,
.link-btn {
  text-decoration: none;
  color: #eaf2ff;
  background: none;
  border: none;
  padding: 0.15rem 0.2rem;
  cursor: pointer;
  font: inherit;
}

a.router-link-active {
  color: #84d1ff;
}

a:hover,
.link-btn:hover {
  color: #b6e3ff;
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
