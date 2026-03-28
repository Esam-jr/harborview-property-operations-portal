import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./assets/main.css";
import { initializePwa } from "./services/pwaService";

createApp(App).use(router).mount("#app");
initializePwa().catch(() => {});
