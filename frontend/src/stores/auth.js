import { reactive } from "vue";

const state = reactive({
  token: localStorage.getItem("hv_token") || "",
  username: localStorage.getItem("hv_username") || "",
  role: localStorage.getItem("hv_role") || "",
});

function setAuth({ token, username, role }) {
  state.token = token;
  state.username = username;
  state.role = role;

  localStorage.setItem("hv_token", token);
  localStorage.setItem("hv_username", username);
  localStorage.setItem("hv_role", role);
}

function clearAuth() {
  state.token = "";
  state.username = "";
  state.role = "";

  localStorage.removeItem("hv_token");
  localStorage.removeItem("hv_username");
  localStorage.removeItem("hv_role");
}

function isAuthenticated() {
  return Boolean(state.token);
}

export function useAuthStore() {
  return {
    state,
    setAuth,
    clearAuth,
    isAuthenticated,
  };
}
