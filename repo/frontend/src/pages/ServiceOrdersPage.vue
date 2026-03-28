<template>
  <section>
    <h2>Service Orders</h2>

    <div class="card" v-if="canCreate">
      <h3>Create Service Order</h3>
      <form class="form-grid" @submit.prevent="submitOrder">
        <label>
          Title
          <input v-model="createForm.title" required minlength="3" />
        </label>
        <label>
          Description
          <textarea v-model="createForm.description" required minlength="3"></textarea>
        </label>
        <button type="submit" :disabled="saving">{{ saving ? "Saving..." : "Create Order" }}</button>
      </form>
    </div>

    <div class="card">
      <div class="list-head">
        <h3>Orders</h3>
        <button type="button" @click="loadOrders">Refresh</button>
      </div>
      <p v-if="error" class="error-text">{{ error }}</p>

      <div class="table-wrap" v-if="orders.length">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Status</th>
              <th>Resident</th>
              <th>Dispatcher</th>
              <th>History</th>
              <th v-if="canUpdateStatus">Update</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in orders" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.title }}</td>
              <td>{{ item.status }}</td>
              <td>{{ item.resident_user_id }}</td>
              <td>{{ item.assigned_to_user_id || "-" }}</td>
              <td>{{ item.status_history?.length || 0 }} events</td>
              <td v-if="canUpdateStatus">
                <div class="inline-group">
                  <select v-model="statusMap[item.id]">
                    <option value="pending">pending</option>
                    <option value="in_progress">in_progress</option>
                    <option value="completed">completed</option>
                  </select>
                  <input
                    v-model="assigneeMap[item.id]"
                    type="number"
                    min="1"
                    placeholder="Dispatcher ID"
                  />
                  <button type="button" @click="updateStatus(item.id)">Apply</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else>No service orders yet.</p>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { createOrder, getOrders, updateOrderStatus } from "../services/orderService";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();

const canCreate = computed(() => auth.state.role === "resident");
const canUpdateStatus = computed(() => ["admin", "manager", "dispatcher"].includes(auth.state.role));

const createForm = reactive({
  title: "",
  description: "",
});

const orders = ref([]);
const error = ref("");
const saving = ref(false);
const statusMap = reactive({});
const assigneeMap = reactive({});

function hydrateControlValues(items) {
  items.forEach((item) => {
    statusMap[item.id] = item.status;
    assigneeMap[item.id] = item.assigned_to_user_id || "";
  });
}

async function loadOrders() {
  try {
    error.value = "";
    const data = await getOrders();
    orders.value = data;
    hydrateControlValues(data);
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to load orders";
  }
}

async function submitOrder() {
  saving.value = true;
  try {
    await createOrder({ ...createForm });
    createForm.title = "";
    createForm.description = "";
    await loadOrders();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to create order";
  } finally {
    saving.value = false;
  }
}

async function updateStatus(orderId) {
  try {
    const payload = {
      status: statusMap[orderId],
    };

    if (assigneeMap[orderId] !== "") {
      payload.assigned_to_user_id = Number(assigneeMap[orderId]);
    }

    await updateOrderStatus(orderId, payload);
    await loadOrders();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to update order status";
  }
}

onMounted(loadOrders);
</script>
