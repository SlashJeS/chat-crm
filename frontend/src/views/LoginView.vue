<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth.store";
import type { UserRole } from "@/types/auth";

const router = useRouter();
const auth = useAuthStore();

const username = ref("");
const password = ref("");

function redirectForRole(role: UserRole): void {
  if (role === "CHATTER") {
    router.push("/chatter");
    return;
  }
  router.push("/teamlead");
}

async function handleSubmit(): Promise<void> {
  try {
    await auth.login(username.value, password.value);
    if (auth.user) {
      redirectForRole(auth.user.role);
    }
  } catch {
    // error is stored in auth.error
  }
}
</script>

<template>
  <div class="login-view">
    <h1>Login</h1>
    <form class="login-form" @submit.prevent="handleSubmit">
      <label>
        Username
        <input v-model="username" type="text" autocomplete="username" required />
      </label>
      <label>
        Password
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
        />
      </label>
      <p v-if="auth.error" class="login-error">{{ auth.error }}</p>
      <button type="submit" :disabled="auth.isLoading">
        {{ auth.isLoading ? "Signing in..." : "Sign in" }}
      </button>
    </form>
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

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 320px;
}

.login-form label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.login-form input {
  padding: 0.5rem;
}

.login-error {
  color: #c0392b;
  margin: 0;
}
</style>
