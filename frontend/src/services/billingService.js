import api from "./api";

export async function getBillingRecords() {
  const response = await api.get("/billing");
  return response.data;
}

export async function createBillingRecord(payload) {
  const response = await api.post("/billing", payload);
  return response.data;
}

export async function uploadProof(billingId, formData) {
  const response = await api.post(`/billing/${billingId}/upload-proof`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function requestRefund(billingId, payload) {
  const response = await api.post(`/billing/${billingId}/refund`, payload);
  return response.data;
}

export async function downloadStatement(billingId, format = "json") {
  const response = await api.get(`/billing/${billingId}/statement`, {
    params: { format },
    responseType: format === "pdf" ? "blob" : "json",
  });
  return response.data;
}
