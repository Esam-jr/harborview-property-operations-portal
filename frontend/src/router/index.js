import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../pages/HomePage.vue";
import DashboardPage from "../pages/DashboardPage.vue";
import ListingsPage from "../pages/ListingsPage.vue";
import ServiceOrdersPage from "../pages/ServiceOrdersPage.vue";

const routes = [
  { path: "/", name: "home", component: HomePage },
  { path: "/dashboard", name: "dashboard", component: DashboardPage },
  { path: "/listings", name: "listings", component: ListingsPage },
  { path: "/service-orders", name: "service-orders", component: ServiceOrdersPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
