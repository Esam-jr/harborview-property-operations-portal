import { reactive } from "vue";

const ENABLE_OFFLINE_MODE = String(import.meta.env.VITE_ENABLE_OFFLINE_MODE || "").toLowerCase() === "true";
const APP_VERSION = import.meta.env.VITE_APP_VERSION || "v1";
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

let deferredInstallPrompt = null;

export const pwaState = reactive({
  enabled: ENABLE_OFFLINE_MODE,
  swRegistered: false,
  installable: false,
  installed: false,
  online: typeof navigator !== "undefined" ? navigator.onLine : true,
});

function hasStandaloneDisplayMode() {
  return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
}

export async function initializePwa() {
  if (typeof window === "undefined") return;

  pwaState.online = window.navigator.onLine;
  window.addEventListener("online", () => {
    pwaState.online = true;
  });
  window.addEventListener("offline", () => {
    pwaState.online = false;
  });

  pwaState.installed = hasStandaloneDisplayMode();

  if (!("serviceWorker" in navigator)) return;

  if (!ENABLE_OFFLINE_MODE) {
    const registrations = await navigator.serviceWorker.getRegistrations();
    await Promise.all(registrations.map((registration) => registration.unregister()));
    pwaState.swRegistered = false;
    pwaState.installable = false;
    return;
  }

  const swUrl = `/sw.js?v=${encodeURIComponent(APP_VERSION)}&apiBase=${encodeURIComponent(API_BASE)}`;
  await navigator.serviceWorker.register(swUrl);
  pwaState.swRegistered = true;

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    pwaState.installable = true;
  });

  window.addEventListener("appinstalled", () => {
    deferredInstallPrompt = null;
    pwaState.installable = false;
    pwaState.installed = true;
  });
}

export async function installOfflineApp() {
  if (!deferredInstallPrompt) return false;
  deferredInstallPrompt.prompt();
  const result = await deferredInstallPrompt.userChoice;
  deferredInstallPrompt = null;
  pwaState.installable = false;
  return result.outcome === "accepted";
}
