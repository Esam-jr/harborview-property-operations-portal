import { createRouter, createWebHistory } from "vue-router";

import BillingPage from "../pages/BillingPage.vue";
import DashboardPage from "../pages/DashboardPage.vue";
import HomePage from "../pages/HomePage.vue";
import ListingsPage from "../pages/ListingsPage.vue";
import LoginPage from "../pages/LoginPage.vue";
import ResidentDashboardPage from "../pages/ResidentDashboardPage.vue";
import ServiceOrdersPage from "../pages/ServiceOrdersPage.vue";
import { useAuthStore } from "../stores/auth";

const routes = [
  { path: "/", redirect: "/home" },
  { path: "/login", name: "login", component: LoginPage, meta: { public: true } },
  {
    path: "/home",
    name: "home",
    component: HomePage,
    meta: { roles: ["admin", "manager", "clerk", "dispatcher", "resident"] },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: DashboardPage,
    meta: { roles: ["admin", "manager", "clerk", "dispatcher", "resident"] },
  },
  {
    path: "/resident-dashboard",
    name: "resident-dashboard",
    component: ResidentDashboardPage,
    meta: { roles: ["resident"] },
  },
  {
    path: "/listings",
    name: "listings",
    component: ListingsPage,
    meta: { roles: ["manager"] },
  },
  {
    path: "/service-orders",
    name: "service-orders",
    component: ServiceOrdersPage,
    meta: { roles: ["admin", "manager", "dispatcher", "resident"] },
  },
  {
    path: "/billing",
    name: "billing",
    component: BillingPage,
    meta: { roles: ["admin", "manager", "clerk", "resident"] },
  },
  { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const { isAuthenticated, state } = useAuthStore();

  if (!to.meta.public && !isAuthenticated()) {
    return { name: "login" };
  }

  if (to.name === "login" && isAuthenticated()) {
    return { name: "home" };
  }

  const allowedRoles = to.meta.roles;
  if (Array.isArray(allowedRoles) && allowedRoles.length > 0) {
    if (!allowedRoles.includes(state.role)) {
      return { name: "dashboard", query: { denied: "1" } };
    }
  }

  return true;
});

export default router;
