<template>
  <section class="card login-wrap">
    <h2>Sign In</h2>
    <form @submit.prevent="handleLogin" class="form-grid">
      <label>
        Username
        <input v-model="form.username" required />
      </label>

      <label>
        Password
        <input v-model="form.password" type="password" minlength="8" required />
      </label>

      <button :class="{ 'is-loading': loading }" :disabled="loading">
        {{ loading ? "Signing in..." : "Login" }}
      </button>
    </form>
    <p v-if="error" class="error-text">{{ error }}</p>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { fetchProtectedUser, login } from "../services/authService";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

const form = reactive({
  username: "",
  password: "",
});

const loading = ref(false);
const error = ref("");

async function handleLogin() {
  loading.value = true;
  error.value = "";

  try {
    const loginResult = await login({
      username: form.username,
      password: form.password,
    });

    auth.setAuth({ token: loginResult.access_token, username: form.username, role: "" });

    try {
      const me = await fetchProtectedUser();
      auth.setAuth({
        token: loginResult.access_token,
        username: me.user?.username || form.username,
        role: me.user?.role || "resident",
      });
    } catch {
      auth.setAuth({ token: loginResult.access_token, username: form.username, role: "resident" });
    }

    router.push({ name: "dashboard" });
  } catch (err) {
    error.value = err?.response?.data?.detail || "Login failed";
  } finally {
    loading.value = false;
  }
}
</script>
