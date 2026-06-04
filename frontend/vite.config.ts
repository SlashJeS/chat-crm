import { fileURLToPath, URL } from "node:url";
import path from "node:path";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

const frontendRoot = fileURLToPath(new URL(".", import.meta.url));
const repoRoot = path.resolve(frontendRoot, "..");

export default defineConfig({
  plugins: [vue()],
  envDir: repoRoot,
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
  },
});
