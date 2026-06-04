<script setup lang="ts">
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth.store";

const router = useRouter();
const auth = useAuthStore();

function loginAsChatter(): void {
  auth.loginPlaceholder("CHATTER");
  router.push("/chatter");
}

function loginAsTeamlead(): void {
  auth.loginPlaceholder("TEAMLEAD");
  router.push("/teamlead");
}
</script>

<template>
  <div class="login-view">
    <h1>Login</h1>
    <button type="button" @click="loginAsChatter">Login as Chatter</button>
    <button type="button" @click="loginAsTeamlead">Login as Teamlead</button>
  </div>
</template>

<style scoped>
.login-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}
</style>
