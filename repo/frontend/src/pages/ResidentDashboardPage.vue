<template>
  <section>
    <h2>Resident Dashboard</h2>

    <div class="card" v-if="!isResident">
      <p>This dashboard is available for resident accounts only.</p>
    </div>

    <template v-else>
      <div class="card">
        <h3>Mailing & Shipping Address</h3>
        <form class="form-grid" @submit.prevent="saveAddresses">
          <label>
            Shipping Address
            <textarea v-model="addressForm.shipping_address" rows="3"></textarea>
          </label>
          <label>
            Mailing Address
            <textarea v-model="addressForm.mailing_address" rows="3"></textarea>
          </label>
          <button type="submit" :disabled="savingAddress">
            {{ savingAddress ? "Saving..." : "Save Addresses" }}
          </button>
        </form>
      </div>

      <div class="card">
        <div class="list-head">
          <h3>Billing Statements</h3>
          <button type="button" @click="loadBilling">Refresh</button>
        </div>

        <div class="table-wrap" v-if="billingRecords.length">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Reference</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in billingRecords" :key="record.id">
                <td>{{ record.id }}</td>
                <td>{{ record.reference_code }}</td>
                <td>{{ record.amount_due }}</td>
                <td>
                  <span class="badge" :class="`badge-${record.status}`">{{ record.status }}</span>
                </td>
                <td>
                  <div class="inline-group">
                    <button type="button" @click="viewStatement(record.id)">View</button>
                    <button type="button" @click="downloadStatementPdf(record.id)">Download PDF</button>
                    <button type="button" @click="openProof(record.id)">Upload Proof</button>
                    <button type="button" @click="openRefund(record.id)">Request Refund</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else>No billing records found.</p>
      </div>

      <div class="card" v-if="proofTargetId !== null">
        <h3>Submit Payment Evidence (Scanned Image)</h3>
        <form class="form-grid" @submit.prevent="submitProof">
          <label>
            Payment Method
            <select v-model="proofForm.payment_method">
              <option value="check">check</option>
              <option value="money_order">money_order</option>
            </select>
          </label>
          <label>
            Amount
            <input v-model="proofForm.amount" type="number" min="0.01" step="0.01" required />
          </label>
          <label>
            Payment Date
            <input v-model="proofForm.payment_date" type="date" required />
          </label>
          <label>
            Reference Number
            <input v-model="proofForm.reference_number" />
          </label>
          <label>
            Scanned Image (JPG/PNG, max 10MB)
            <input type="file" accept="image/jpeg,image/png" @change="onProofFileChange" required />
          </label>
          <div class="inline-group">
            <button type="submit" :disabled="savingProof">{{ savingProof ? "Uploading..." : "Submit Proof" }}</button>
            <button type="button" @click="closeProof">Cancel</button>
          </div>
        </form>
      </div>

      <div class="card" v-if="refundTargetId !== null">
        <h3>Request Refund as Credit</h3>
        <form class="form-grid" @submit.prevent="submitRefund">
          <label>
            Credit Amount
            <input v-model="refundForm.amount" type="number" min="0.01" step="0.01" required />
          </label>
          <label>
            Reason
            <textarea v-model="refundForm.reason" minlength="3" required></textarea>
          </label>
          <div class="inline-group">
            <button type="submit" :disabled="savingRefund">
              {{ savingRefund ? "Submitting..." : "Request Refund" }}
            </button>
            <button type="button" @click="closeRefund">Cancel</button>
          </div>
        </form>
      </div>

      <div class="card">
        <div class="list-head">
          <h3>Service Orders</h3>
          <button type="button" @click="loadOrders">Refresh</button>
        </div>

        <div class="table-wrap" v-if="orders.length">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Status</th>
                <th>Milestones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders" :key="order.id">
                <td>{{ order.id }}</td>
                <td>{{ order.title }}</td>
                <td>
                  <span class="badge" :class="`badge-${order.status}`">{{ order.status }}</span>
                </td>
                <td>
                  <ul class="flat-list compact-list">
                    <li v-for="step in order.status_history" :key="step.id">
                      <span class="badge" :class="`badge-${step.status}`">{{ step.status }}</span>
                      <span> - {{ formatDate(step.changed_at) }}</span>
                    </li>
                  </ul>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else>No service orders found.</p>
      </div>

      <div class="card" v-if="selectedStatement">
        <h3>Statement Details</h3>
        <ul class="flat-list compact-list">
          <li><strong>Billing ID:</strong> {{ selectedStatement.billing_id }}</li>
          <li><strong>Reference:</strong> {{ selectedStatement.reference_code }}</li>
          <li><strong>Amount Due:</strong> {{ selectedStatement.amount_due }}</li>
          <li><strong>Due Date:</strong> {{ selectedStatement.due_date }}</li>
          <li>
            <strong>Status:</strong>
            <span class="badge" :class="`badge-${selectedStatement.status}`">{{ selectedStatement.status }}</span>
          </li>
          <li><strong>Notes:</strong> {{ selectedStatement.notes || "-" }}</li>
        </ul>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import {
  downloadStatement,
  getBillingRecords,
  requestRefund,
  uploadProof,
} from "../services/billingService";
import { getOrders } from "../services/orderService";
import { getResidentProfile, updateResidentAddress } from "../services/residentService";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const isResident = computed(() => auth.state.role === "resident");

const error = ref("");

const addressForm = reactive({
  shipping_address: "",
  mailing_address: "",
});
const savingAddress = ref(false);

const billingRecords = ref([]);
const proofTargetId = ref(null);
const savingProof = ref(false);
const proofFile = ref(null);
const proofForm = reactive({
  payment_method: "check",
  amount: "",
  payment_date: "",
  reference_number: "",
});

const refundTargetId = ref(null);
const savingRefund = ref(false);
const refundForm = reactive({
  amount: "",
  reason: "",
});

const selectedStatement = ref(null);
const orders = ref([]);

function formatDate(isoDate) {
  return new Date(isoDate).toLocaleString();
}

async function loadResidentProfile() {
  try {
    const data = await getResidentProfile();
    addressForm.shipping_address = data.shipping_address || "";
    addressForm.mailing_address = data.mailing_address || "";
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to load resident profile";
  }
}

async function saveAddresses() {
  savingAddress.value = true;
  error.value = "";
  try {
    await updateResidentAddress({
      shipping_address: addressForm.shipping_address || null,
      mailing_address: addressForm.mailing_address || null,
    });
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to update addresses";
  } finally {
    savingAddress.value = false;
  }
}

async function loadBilling() {
  try {
    billingRecords.value = await getBillingRecords();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to load billing records";
  }
}

function openProof(billingId) {
  proofTargetId.value = billingId;
}

function closeProof() {
  proofTargetId.value = null;
  proofFile.value = null;
  proofForm.payment_method = "check";
  proofForm.amount = "";
  proofForm.payment_date = "";
  proofForm.reference_number = "";
}

function onProofFileChange(event) {
  const nextFile = event.target.files?.[0] || null;
  if (!nextFile) {
    proofFile.value = null;
    return;
  }

  const allowedTypes = ["image/jpeg", "image/png"];
  const maxSize = 10 * 1024 * 1024;

  if (!allowedTypes.includes(nextFile.type)) {
    error.value = "Unsupported proof format. Allowed: JPG, PNG";
    proofFile.value = null;
    event.target.value = "";
    return;
  }

  if (nextFile.size > maxSize) {
    error.value = "Proof image exceeds 10MB limit";
    proofFile.value = null;
    event.target.value = "";
    return;
  }

  error.value = "";
  proofFile.value = nextFile;
}

async function submitProof() {
  if (!proofTargetId.value || !proofFile.value) {
    error.value = "Please attach a scanned image proof file.";
    return;
  }

  savingProof.value = true;
  error.value = "";
  try {
    const formData = new FormData();
    formData.append("payment_method", proofForm.payment_method);
    formData.append("amount", proofForm.amount);
    formData.append("payment_date", proofForm.payment_date);
    if (proofForm.reference_number) {
      formData.append("reference_number", proofForm.reference_number);
    }
    formData.append("proof_file", proofFile.value);

    await uploadProof(proofTargetId.value, formData);
    closeProof();
    await loadBilling();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to submit payment evidence";
  } finally {
    savingProof.value = false;
  }
}

function openRefund(billingId) {
  refundTargetId.value = billingId;
}

function closeRefund() {
  refundTargetId.value = null;
  refundForm.amount = "";
  refundForm.reason = "";
}

async function submitRefund() {
  if (!refundTargetId.value) return;

  savingRefund.value = true;
  error.value = "";
  try {
    await requestRefund(refundTargetId.value, {
      amount: refundForm.amount,
      reason: refundForm.reason,
    });
    closeRefund();
    await loadBilling();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to request refund";
  } finally {
    savingRefund.value = false;
  }
}

async function viewStatement(billingId) {
  try {
    selectedStatement.value = await downloadStatement(billingId, "json");
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to load statement";
  }
}

async function downloadStatementPdf(billingId) {
  try {
    const blob = await downloadStatement(billingId, "pdf");
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `statement-${billingId}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to download PDF statement";
  }
}

async function loadOrders() {
  try {
    orders.value = await getOrders();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to load service orders";
  }
}

onMounted(async () => {
  if (!isResident.value) return;

  await loadResidentProfile();
  await loadBilling();
  await loadOrders();
});
</script>
