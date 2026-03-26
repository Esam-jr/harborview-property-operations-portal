<template>
  <section>
    <h2>Listings</h2>

    <div class="card" v-if="canEdit">
      <h3>Create Listing</h3>
      <form class="form-grid" @submit.prevent="createNewListing">
        <label>
          Title
          <input v-model="createForm.title" required minlength="3" />
        </label>
        <label>
          Description
          <textarea v-model="createForm.description" required minlength="3"></textarea>
        </label>
        <label>
          Price Amount
          <input v-model="createForm.price_amount" type="number" min="0" step="0.01" />
        </label>
        <label>
          Status
          <select v-model="createForm.status">
            <option value="draft">draft</option>
            <option value="published">published</option>
            <option value="unpublished">unpublished</option>
          </select>
        </label>
        <label>
          Media Files
          <input type="file" multiple @change="onCreateFiles" />
        </label>
        <button type="submit" :disabled="saving">{{ saving ? "Saving..." : "Create" }}</button>
      </form>
    </div>

    <div class="card">
      <div class="list-head">
        <h3>All Listings</h3>
        <button type="button" @click="loadListings">Refresh</button>
      </div>
      <p v-if="error" class="error-text">{{ error }}</p>

      <table class="table" v-if="listings.length">
        <thead>
          <tr>
            <th></th>
            <th>ID</th>
            <th>Title</th>
            <th>Status</th>
            <th>Owner</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in listings" :key="item.id">
            <td><input type="checkbox" :value="item.id" v-model="selectedIds" /></td>
            <td>{{ item.id }}</td>
            <td>{{ item.title }}</td>
            <td>{{ item.status }}</td>
            <td>{{ item.owner_user_id }}</td>
            <td>
              <button v-if="canEdit" type="button" @click="openEdit(item)">Edit</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No listings yet.</p>

      <div v-if="canEdit" class="inline-group">
        <select v-model="bulkStatus">
          <option value="draft">draft</option>
          <option value="published">published</option>
          <option value="unpublished">unpublished</option>
        </select>
        <button type="button" @click="applyBulk">Bulk Update</button>
      </div>
    </div>

    <div class="card" v-if="editingItem && canEdit">
      <h3>Edit Listing #{{ editingItem.id }}</h3>
      <form class="form-grid" @submit.prevent="submitEdit">
        <label>
          Title
          <input v-model="editForm.title" minlength="3" />
        </label>
        <label>
          Description
          <textarea v-model="editForm.description" minlength="3"></textarea>
        </label>
        <label>
          Price Amount
          <input v-model="editForm.price_amount" type="number" min="0" step="0.01" />
        </label>
        <label>
          Status
          <select v-model="editForm.status">
            <option value="">No change</option>
            <option value="draft">draft</option>
            <option value="published">published</option>
            <option value="unpublished">unpublished</option>
          </select>
        </label>
        <label>
          New Media Files
          <input type="file" multiple @change="onEditFiles" />
        </label>
        <div class="inline-group">
          <button type="submit" :disabled="saving">{{ saving ? "Updating..." : "Update" }}</button>
          <button type="button" @click="cancelEdit">Cancel</button>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import {
  bulkUpdateListings,
  createListing,
  getListings,
  updateListing,
} from "../services/listingService";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();

const canEdit = computed(() => ["admin", "manager", "clerk", "resident"].includes(auth.state.role));

const listings = ref([]);
const selectedIds = ref([]);
const bulkStatus = ref("published");
const saving = ref(false);
const error = ref("");

const createFiles = ref([]);
const editFiles = ref([]);
const editingItem = ref(null);

const createForm = reactive({
  title: "",
  description: "",
  price_amount: "",
  status: "draft",
});

const editForm = reactive({
  title: "",
  description: "",
  price_amount: "",
  status: "",
});

function onCreateFiles(event) {
  createFiles.value = Array.from(event.target.files || []);
}

function onEditFiles(event) {
  editFiles.value = Array.from(event.target.files || []);
}

function resetCreateForm() {
  createForm.title = "";
  createForm.description = "";
  createForm.price_amount = "";
  createForm.status = "draft";
  createFiles.value = [];
}

function openEdit(item) {
  editingItem.value = item;
  editForm.title = item.title;
  editForm.description = item.description;
  editForm.price_amount = item.price_amount ?? "";
  editForm.status = "";
  editFiles.value = [];
}

function cancelEdit() {
  editingItem.value = null;
}

function toFormData(form, files) {
  const fd = new FormData();
  if (form.title !== undefined && form.title !== "") fd.append("title", form.title);
  if (form.description !== undefined && form.description !== "") fd.append("description", form.description);
  if (form.price_amount !== undefined && form.price_amount !== "") fd.append("price_amount", form.price_amount);
  if (form.status !== undefined && form.status !== "") fd.append("status", form.status);
  files.forEach((file) => fd.append("files", file));
  return fd;
}

async function loadListings() {
  try {
    error.value = "";
    listings.value = await getListings();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to load listings";
  }
}

async function createNewListing() {
  saving.value = true;
  try {
    const fd = toFormData(createForm, createFiles.value);
    await createListing(fd);
    resetCreateForm();
    await loadListings();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to create listing";
  } finally {
    saving.value = false;
  }
}

async function submitEdit() {
  if (!editingItem.value) return;
  saving.value = true;
  try {
    const fd = toFormData(editForm, editFiles.value);
    await updateListing(editingItem.value.id, fd);
    editingItem.value = null;
    await loadListings();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to update listing";
  } finally {
    saving.value = false;
  }
}

async function applyBulk() {
  if (!selectedIds.value.length) {
    error.value = "Select at least one listing for bulk update";
    return;
  }
  try {
    await bulkUpdateListings({ ids: selectedIds.value, status: bulkStatus.value });
    selectedIds.value = [];
    await loadListings();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to bulk update listings";
  }
}

onMounted(loadListings);
</script>
