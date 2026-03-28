<template>
  <section>
    <h2>Dashboard</h2>
    <p>Welcome back, {{ auth.state.username }}.</p>
    <p>Role: <strong>{{ auth.state.role || "unknown" }}</strong></p>
    <p v-if="accessDenied" class="error-text">You are not allowed to access that page.</p>

    <div class="card">
      <h3>Available Modules</h3>
      <ul class="flat-list">
        <li><router-link to="/home">Home</router-link></li>
        <li v-if="canAccessResidentDashboard"><router-link to="/resident-dashboard">Resident Dashboard</router-link></li>
        <li v-if="canAccessListings"><router-link to="/listings">Listings</router-link></li>
        <li v-if="canAccessOrders"><router-link to="/service-orders">Service Orders</router-link></li>
        <li v-if="canAccessBilling"><router-link to="/billing">Billing</router-link></li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const route = useRoute();

const accessDenied = computed(() => route.query.denied === "1");

const canAccessResidentDashboard = computed(() => auth.state.role === "resident");
const canAccessListings = computed(() => ["manager"].includes(auth.state.role));
const canAccessOrders = computed(() =>
  ["admin", "manager", "dispatcher", "resident"].includes(auth.state.role),
);
const canAccessBilling = computed(() =>
  ["admin", "manager", "clerk", "resident"].includes(auth.state.role),
);
</script>
