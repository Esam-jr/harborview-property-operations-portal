import api from "./api";

export async function login(payload) {
  const response = await api.post("/auth/login", payload);
  return response.data;
}

export async function fetchProtectedUser() {
  const response = await api.get("/protected/me");
  return response.data;
}
