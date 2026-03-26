<template>
  <header class="header">
    <h1>HarborView Portal</h1>
    <nav>
      <router-link to="/">Home</router-link>
      <router-link to="/dashboard">Dashboard</router-link>
      <router-link to="/listings">Listings</router-link>
      <router-link to="/service-orders">Service Orders</router-link>
    </nav>
  </header>
</template>

<style scoped>
.header {
  padding: 1rem 1.5rem;
  background: #0f172a;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

nav {
  display: flex;
  gap: 1rem;
}

a {
  text-decoration: none;
  color: #e2e8f0;
}

a.router-link-active {
  color: #38bdf8;
}
</style>
