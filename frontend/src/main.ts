import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";
import { useThemeStore } from "./stores/theme.store";

import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/utilities.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

useThemeStore(pinia).initTheme();

app.mount("#app");
