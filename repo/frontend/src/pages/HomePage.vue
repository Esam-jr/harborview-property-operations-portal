<template>
  <section>
    <h2>Home</h2>

    <div class="card" v-if="metaMessage">
      <strong>{{ metaMessage }}</strong>
      <p class="small-muted">Source: {{ sourceLabel }}</p>
    </div>

    <div class="card" v-if="sections.carousel_panels?.length">
      <h3>Carousel Panels</h3>
      <div class="simple-grid">
        <article v-for="(panel, idx) in sections.carousel_panels" :key="`panel-${idx}`" class="tile">
          <h4>{{ panel.title || `Panel ${idx + 1}` }}</h4>
          <p>{{ panel.body || panel.description || "No content" }}</p>
        </article>
      </div>
    </div>

    <div class="card" v-if="sections.recommended_tiles?.length">
      <h3>Recommended Tiles</h3>
      <div class="simple-grid">
        <article v-for="(tile, idx) in sections.recommended_tiles" :key="`tile-${idx}`" class="tile">
          <h4>{{ tile.title || `Tile ${idx + 1}` }}</h4>
          <p>{{ tile.body || tile.description || "No content" }}</p>
        </article>
      </div>
    </div>

    <div class="card" v-if="sections.announcement_banners?.length">
      <h3>Announcement Banners</h3>
      <div class="banner-list">
        <div v-for="(banner, idx) in sections.announcement_banners" :key="`banner-${idx}`" class="banner-item">
          <strong>{{ banner.title || `Announcement ${idx + 1}` }}</strong>
          <p>{{ banner.body || banner.message || "No content" }}</p>
        </div>
      </div>
    </div>

    <div class="card" v-if="isAdmin">
      <h3>Admin Homepage Config</h3>
      <form class="form-grid" @submit.prevent="saveConfig">
        <label>
          Staged Carousel Panels (JSON Array)
          <textarea v-model="stagedCarouselJson" rows="6"></textarea>
        </label>
        <label>
          Staged Recommended Tiles (JSON Array)
          <textarea v-model="stagedTilesJson" rows="6"></textarea>
        </label>
        <label>
          Staged Announcement Banners (JSON Array)
          <textarea v-model="stagedBannersJson" rows="6"></textarea>
        </label>

        <label class="inline-check">
          <input type="checkbox" v-model="configFlags.preview_enabled" />
          Preview mode enabled (admins see staged)
        </label>

        <label class="inline-check">
          <input type="checkbox" v-model="configFlags.rollout_enabled" />
          Controlled rollout enabled
        </label>

        <label>
          Rollout percentage for staff (0-100)
          <input v-model.number="configFlags.rollout_percentage" type="number" min="0" max="100" />
        </label>

        <label class="inline-check">
          <input type="checkbox" v-model="configFlags.full_enablement" />
          Full enablement (apply staged to live)
        </label>

        <div class="inline-group">
          <button type="submit" :disabled="saving">{{ saving ? "Saving..." : "Save Config" }}</button>
          <button type="button" @click="reloadConfig">Reload</button>
        </div>
      </form>
      <p v-if="adminError" class="error-text">{{ adminError }}</p>
    </div>

    <p v-if="error" class="error-text">{{ error }}</p>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { getHomePageConfig, getHomePageContent, updateHomePageConfig } from "../services/homepageService";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const isAdmin = computed(() => auth.state.role === "admin");

const sections = reactive({
  carousel_panels: [],
  recommended_tiles: [],
  announcement_banners: [],
});

const source = ref("live");
const error = ref("");
const adminError = ref("");
const saving = ref(false);

const stagedCarouselJson = ref("[]");
const stagedTilesJson = ref("[]");
const stagedBannersJson = ref("[]");

const configFlags = reactive({
  preview_enabled: false,
  rollout_enabled: false,
  rollout_percentage: 10,
  full_enablement: false,
});

const sourceLabel = computed(() => (source.value === "staged" ? "Staged configuration" : "Live configuration"));

const metaMessage = computed(() => {
  if (source.value === "staged") {
    return "Preview/Rollout content is active for your account.";
  }
  return "Live homepage content.";
});

function safeParseArray(value) {
  const parsed = JSON.parse(value);
  if (!Array.isArray(parsed)) {
    throw new Error("Expected a JSON array");
  }
  return parsed;
}

async function loadContent() {
  try {
    error.value = "";
    const data = await getHomePageContent();
    sections.carousel_panels = data.sections.carousel_panels || [];
    sections.recommended_tiles = data.sections.recommended_tiles || [];
    sections.announcement_banners = data.sections.announcement_banners || [];
    source.value = data.source || "live";
  } catch (err) {
    error.value = err?.response?.data?.detail || "Failed to load homepage content";
  }
}

function hydrateAdminForm(config) {
  stagedCarouselJson.value = JSON.stringify(config.staged.carousel_panels || [], null, 2);
  stagedTilesJson.value = JSON.stringify(config.staged.recommended_tiles || [], null, 2);
  stagedBannersJson.value = JSON.stringify(config.staged.announcement_banners || [], null, 2);

  configFlags.preview_enabled = Boolean(config.preview_enabled);
  configFlags.rollout_enabled = Boolean(config.rollout_enabled);
  configFlags.rollout_percentage = Number(config.rollout_percentage ?? 10);
  configFlags.full_enablement = Boolean(config.full_enablement);
}

async function reloadConfig() {
  if (!isAdmin.value) return;

  try {
    adminError.value = "";
    const config = await getHomePageConfig();
    hydrateAdminForm(config);
  } catch (err) {
    adminError.value = err?.response?.data?.detail || "Failed to load homepage config";
  }
}

async function saveConfig() {
  if (!isAdmin.value) return;

  saving.value = true;
  adminError.value = "";

  try {
    const payload = {
      staged: {
        carousel_panels: safeParseArray(stagedCarouselJson.value),
        recommended_tiles: safeParseArray(stagedTilesJson.value),
        announcement_banners: safeParseArray(stagedBannersJson.value),
      },
      preview_enabled: configFlags.preview_enabled,
      rollout_enabled: configFlags.rollout_enabled,
      rollout_percentage: configFlags.rollout_percentage,
      full_enablement: configFlags.full_enablement,
    };

    const updated = await updateHomePageConfig(payload);
    hydrateAdminForm(updated);
    await loadContent();
  } catch (err) {
    if (err instanceof SyntaxError) {
      adminError.value = "Invalid JSON in one or more staged section fields.";
    } else {
      adminError.value = err?.response?.data?.detail || "Failed to save homepage config";
    }
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  await loadContent();
  await reloadConfig();
});
</script>
