import api from "./api";

export async function getListings(params = {}) {
  const response = await api.get("/listings", { params });
  return response.data;
}

export async function createListing(formData) {
  const response = await api.post("/listings", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function updateListing(id, formData) {
  const response = await api.put(`/listings/${id}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function bulkUpdateListings(payload) {
  const response = await api.patch("/listings/bulk-update", payload);
  return response.data;
}
