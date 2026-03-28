import api from "./api";

export async function getResidentProfile() {
  const response = await api.get("/resident/profile");
  return response.data;
}

export async function updateResidentAddress(payload) {
  const response = await api.put("/resident/address", payload);
  return response.data;
}
