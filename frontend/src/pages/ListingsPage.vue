<template>
  <section>
    <h2>Listings</h2>

    <div class="card" v-if="!canManageListings">
      <p>You need manager role to manage marketplace listings.</p>
    </div>

    <template v-else>
      <div class="card">
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

          <p v-if="createFileError" class="error-text">{{ createFileError }}</p>

          <button type="submit" :disabled="saving || Boolean(createFileError)">
            {{ saving ? "Saving..." : "Create" }}
          </button>
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
                <button type="button" @click="openEdit(item)">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else>No listings yet.</p>

        <div class="inline-group">
          <select v-model="bulkStatus">
            <option value="draft">draft</option>
            <option value="published">published</option>
            <option value="unpublished">unpublished</option>
          </select>
          <button type="button" @click="applyBulk">Bulk Update</button>
        </div>
      </div>

      <div class="card" v-if="editingItem">
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

          <p v-if="editFileError" class="error-text">{{ editFileError }}</p>

          <div class="inline-group">
            <button type="submit" :disabled="saving || Boolean(editFileError)">
              {{ saving ? "Updating..." : "Update" }}
            </button>
            <button type="button" @click="cancelEdit">Cancel</button>
          </div>
        </form>
      </div>
    </template>
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

const canManageListings = computed(() => auth.state.role === "manager");

const listings = ref([]);
const selectedIds = ref([]);
const bulkStatus = ref("published");
const saving = ref(false);
const error = ref("");

const createFiles = ref([]);
const editFiles = ref([]);
const createFileError = ref("");
const editFileError = ref("");
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

function validateMediaFiles(files) {
  const allowedImageTypes = ["image/jpeg", "image/png"];
  const allowedVideoTypes = ["video/mp4"];
  const maxImageBytes = 10 * 1024 * 1024;
  const maxVideoBytes = 200 * 1024 * 1024;

  for (const file of files) {
    const isImage = allowedImageTypes.includes(file.type);
    const isVideo = allowedVideoTypes.includes(file.type);

    if (!isImage && !isVideo) {
      return `Unsupported format for ${file.name}. Allowed: JPG, PNG, MP4.`;
    }

    if (isImage && file.size > maxImageBytes) {
      return `Image ${file.name} exceeds 10 MB limit.`;
    }

    if (isVideo && file.size > maxVideoBytes) {
      return `Video ${file.name} exceeds 200 MB limit.`;
    }
  }

  return "";
}

function onCreateFiles(event) {
  const files = Array.from(event.target.files || []);
  createFiles.value = files;
  createFileError.value = validateMediaFiles(files);
}

function onEditFiles(event) {
  const files = Array.from(event.target.files || []);
  editFiles.value = files;
  editFileError.value = validateMediaFiles(files);
}

function resetCreateForm() {
  createForm.title = "";
  createForm.description = "";
  createForm.price_amount = "";
  createForm.status = "draft";
  createFiles.value = [];
  createFileError.value = "";
}

function openEdit(item) {
  editingItem.value = item;
  editForm.title = item.title;
  editForm.description = item.description;
  editForm.price_amount = item.price_amount ?? "";
  editForm.status = "";
  editFiles.value = [];
  editFileError.value = "";
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
  if (!canManageListings.value) return;

  try {
    error.value = "";
    listings.value = await getListings();
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to load listings";
  }
}

async function createNewListing() {
  if (createFileError.value) return;

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
  if (!editingItem.value || editFileError.value) return;

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
