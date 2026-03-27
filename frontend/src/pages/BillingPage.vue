<template>
  <section>
    <h2>Billing</h2>

    <div class="card" v-if="canCreateBilling">
      <h3>Create Billing Record</h3>
      <form class="form-grid" @submit.prevent="submitBilling">
        <label>
          Resident User ID
          <input v-model="createForm.resident_user_id" type="number" min="1" required />
        </label>
        <label>
          Amount Due
          <input v-model="createForm.amount_due" type="number" min="0.01" step="0.01" required />
        </label>
        <label>
          Due Date
          <input v-model="createForm.due_date" type="date" required />
        </label>
        <label>
          Notes
          <textarea v-model="createForm.notes"></textarea>
        </label>
        <button type="submit" :disabled="saving">{{ saving ? "Saving..." : "Create Billing" }}</button>
      </form>
    </div>

    <div class="card">
      <div class="list-head">
        <h3>Billing Records</h3>
        <button type="button" @click="loadBilling">Refresh</button>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>

      <div class="table-wrap" v-if="records.length">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Reference</th>
              <th>Resident</th>
              <th>Amount Due</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in records" :key="record.id">
              <td>{{ record.id }}</td>
              <td>{{ record.reference_code }}</td>
              <td>{{ record.resident_user_id }}</td>
              <td>{{ record.amount_due }}</td>
              <td>{{ record.status }}</td>
              <td>
                <div class="inline-group">
                  <button type="button" @click="openProof(record.id)">Upload Proof</button>
                  <button type="button" @click="openRefund(record.id)">Refund</button>
                  <button type="button" @click="downloadJson(record.id)">Statement JSON</button>
                  <button type="button" @click="downloadPdf(record.id)">Statement PDF</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else>No billing records yet.</p>
    </div>

    <div v-if="proofTargetId !== null" class="card">
      <h3>Upload Payment Proof - Billing #{{ proofTargetId }}</h3>
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
          Proof Image (JPG/PNG)
          <input type="file" accept="image/jpeg,image/png" @change="onProofFileChange" required />
        </label>
        <div class="inline-group">
          <button type="submit" :disabled="saving">Upload</button>
          <button type="button" @click="closeProof">Cancel</button>
        </div>
      </form>
    </div>

    <div v-if="refundTargetId !== null" class="card">
      <h3>Request Refund - Billing #{{ refundTargetId }}</h3>
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
          <button type="submit" :disabled="saving">Request Refund</button>
          <button type="button" @click="closeRefund">Cancel</button>
        </div>
      </form>
    </div>

    <div v-if="statementJson" class="card">
      <h3>Statement JSON</h3>
      <pre>{{ statementJson }}</pre>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import {
  createBillingRecord,
  downloadStatement,
  getBillingRecords,
  requestRefund,
  uploadProof,
} from "../services/billingService";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();

const canCreateBilling = computed(() => ["admin", "manager", "clerk"].includes(auth.state.role));

const records = ref([]);
const error = ref("");
const saving = ref(false);
const statementJson = ref("");

const createForm = reactive({
  resident_user_id: "",
  amount_due: "",
  due_date: "",
  notes: "",
});

const proofTargetId = ref(null);
const proofFile = ref(null);
const proofForm = reactive({
  payment_method: "check",
  amount: "",
  payment_date: "",
  reference_number: "",
});

const refundTargetId = ref(null);
const refundForm = reactive({
  amount: "",
  reason: "",
});

function resetCreateForm() {
  createForm.resident_user_id = "";
  createForm.amount_due = "";
  createForm.due_date = "";
  createForm.notes = "";
}

function openProof(id) {
  proofTargetId.value = id;
}

function closeProof() {
  proofTargetId.value = null;
  proofFile.value = null;
  proofForm.payment_method = "check";
  proofForm.amount = "";
  proofForm.payment_date = "";
  proofForm.reference_number = "";
}

function openRefund(id) {
  refundTargetId.value = id;
}

function closeRefund() {
  refundTargetId.value = null;
  refundForm.amount = "";
  refundForm.reason = "";
}

function onProofFileChange(event) {
  proofFile.value = event.target.files?.[0] || null;
}

async function loadBilling() {
  try {
    error.value = "";
    records.value = await getBillingRecords();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to load billing records";
  }
}

async function submitBilling() {
  saving.value = true;
  try {
    await createBillingRecord({
      resident_user_id: Number(createForm.resident_user_id),
      amount_due: createForm.amount_due,
      due_date: createForm.due_date,
      notes: createForm.notes || null,
    });
    resetCreateForm();
    await loadBilling();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to create billing record";
  } finally {
    saving.value = false;
  }
}

async function submitProof() {
  if (!proofTargetId.value || !proofFile.value) {
    error.value = "Select a proof file first";
    return;
  }

  saving.value = true;
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
    error.value = err?.response?.data?.detail || "Failed to upload payment proof";
  } finally {
    saving.value = false;
  }
}

async function submitRefund() {
  if (!refundTargetId.value) return;

  saving.value = true;
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
    saving.value = false;
  }
}

async function downloadJson(id) {
  try {
    const data = await downloadStatement(id, "json");
    statementJson.value = JSON.stringify(data, null, 2);
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to download statement JSON";
  }
}

async function downloadPdf(id) {
  try {
    const blob = await downloadStatement(id, "pdf");
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `billing-${id}-statement.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to download statement PDF";
  }
}

onMounted(loadBilling);
</script>
