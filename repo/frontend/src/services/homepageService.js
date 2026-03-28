import api from "./api";

export async function getHomePageContent() {
  const response = await api.get("/homepage");
  return response.data;
}

export async function getHomePageConfig() {
  const response = await api.get("/homepage/config");
  return response.data;
}

export async function updateHomePageConfig(payload) {
  const response = await api.put("/homepage/config", payload);
  return response.data;
}
