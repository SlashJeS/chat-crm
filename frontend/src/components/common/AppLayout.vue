<script setup lang="ts">
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth.store";

const router = useRouter();
const auth = useAuthStore();

function logout(): void {
  auth.logout();
  router.push("/login");
}
</script>

<template>
  <div class="app-layout">
    <header class="app-layout__header">
      <span>CRM Chatters Demo</span>
      <button v-if="auth.isAuthenticated" type="button" @click="logout">Logout</button>
    </header>
    <main class="app-layout__main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-layout__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #ddd;
}

.app-layout__main {
  flex: 1;
  padding: 1rem;
}
</style>
