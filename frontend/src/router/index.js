import { createRouter, createWebHistory } from "vue-router";

import BillingPage from "../pages/BillingPage.vue";
import DashboardPage from "../pages/DashboardPage.vue";
import ListingsPage from "../pages/ListingsPage.vue";
import LoginPage from "../pages/LoginPage.vue";
import ServiceOrdersPage from "../pages/ServiceOrdersPage.vue";
import { useAuthStore } from "../stores/auth";

const routes = [
  { path: "/", redirect: "/dashboard" },
  { path: "/login", name: "login", component: LoginPage, meta: { public: true } },
  {
    path: "/dashboard",
    name: "dashboard",
    component: DashboardPage,
    meta: { roles: ["admin", "manager", "clerk", "dispatcher", "resident"] },
  },
  {
    path: "/listings",
    name: "listings",
    component: ListingsPage,
    meta: { roles: ["admin", "manager", "clerk", "dispatcher", "resident"] },
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
    return { name: "dashboard" };
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
