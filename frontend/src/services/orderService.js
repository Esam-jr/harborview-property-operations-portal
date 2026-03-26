import api from "./api";

export async function getOrders() {
  const response = await api.get("/orders");
  return response.data;
}

export async function createOrder(payload) {
  const response = await api.post("/orders", payload);
  return response.data;
}

export async function updateOrderStatus(id, payload) {
  const response = await api.patch(`/orders/${id}/status`, payload);
  return response.data;
}
