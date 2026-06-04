<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import LoadingState from "@/components/common/LoadingState.vue";
import { useAuthStore } from "@/stores/auth.store";
import type { UserRole } from "@/types/auth";

const router = useRouter();
const auth = useAuthStore();

const username = ref("");
const password = ref("");

const demoAccounts = [
  { label: "Teamlead", username: "lead", password: "password123", role: "TEAMLEAD" as UserRole },
  { label: "Chatter 1", username: "chatter1", password: "password123", role: "CHATTER" as UserRole },
  { label: "Chatter 2", username: "chatter2", password: "password123", role: "CHATTER" as UserRole },
  { label: "Chatter 3", username: "chatter3", password: "password123", role: "CHATTER" as UserRole },
];

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
    // error stored in auth.error
  }
}

function fillDemo(account: (typeof demoAccounts)[number]): void {
  username.value = account.username;
  password.value = account.password;
}

async function loginAsDemo(account: (typeof demoAccounts)[number]): Promise<void> {
  username.value = account.username;
  password.value = account.password;
  await handleSubmit();
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <header class="login-card__header">
        <h1>CRM Chatters Demo</h1>
        <p>
          Mini CRM workspace for chatters and teamleads. Sign in with a demo account to explore
          live chat, presence, and monitor dashboards.
        </p>
      </header>

      <LoadingState v-if="auth.isLoading" message="Signing in..." />

      <form v-else class="login-form" @submit.prevent="handleSubmit">
        <label class="login-form__field">
          <span>Username</span>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="e.g. chatter1"
            required
          />
        </label>
        <label class="login-form__field">
          <span>Password</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="password123"
            required
          />
        </label>

        <p v-if="auth.error" class="login-form__error">{{ auth.error }}</p>

        <button type="submit" class="login-form__submit" :disabled="auth.isLoading">
          Sign in
        </button>
      </form>

      <section class="login-demo">
        <h2>Demo accounts</h2>
        <p class="login-demo__hint">All demo passwords are <code>password123</code></p>
        <ul class="login-demo__list">
          <li v-for="account in demoAccounts" :key="account.username">
            <span class="login-demo__account">
              <strong>{{ account.label }}</strong>
              <span>{{ account.username }} / password123</span>
            </span>
            <div class="login-demo__actions">
              <button type="button" class="login-demo__fill" @click="fillDemo(account)">
                Fill
              </button>
              <button
                type="button"
                class="login-demo__sign-in"
                :disabled="auth.isLoading"
                @click="loginAsDemo(account)"
              >
                Sign in
              </button>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 2rem 1rem;
}

.login-card {
  width: 100%;
  max-width: 480px;
  padding: 2rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  background: #fff;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.login-card__header h1 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
}

.login-card__header p {
  margin: 0;
  color: #64748b;
  line-height: 1.5;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.5rem;
}

.login-form__field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.9rem;
  color: #334155;
}

.login-form__field input {
  padding: 0.6rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
}

.login-form__field input:focus {
  outline: 2px solid #93c5fd;
  border-color: #60a5fa;
}

.login-form__error {
  margin: 0;
  padding: 0.65rem 0.75rem;
  border-radius: 0.375rem;
  background: #fdecea;
  color: #c0392b;
  font-size: 0.9rem;
}

.login-form__submit {
  padding: 0.65rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background: #2563eb;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.login-form__submit:hover:not(:disabled) {
  background: #1d4ed8;
}

.login-demo {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.login-demo h2 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
}

.login-demo__hint {
  margin: 0 0 1rem;
  color: #64748b;
  font-size: 0.85rem;
}

.login-demo__hint code {
  padding: 0.1rem 0.35rem;
  border-radius: 0.25rem;
  background: #f1f5f9;
  font-size: 0.85rem;
}

.login-demo__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.login-demo__list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  background: #f8fafc;
}

.login-demo__account {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.85rem;
  color: #64748b;
}

.login-demo__account strong {
  color: #0f172a;
}

.login-demo__actions {
  display: flex;
  gap: 0.35rem;
  flex-shrink: 0;
}

.login-demo__fill,
.login-demo__sign-in {
  padding: 0.35rem 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  background: #fff;
  font-size: 0.8rem;
  cursor: pointer;
}

.login-demo__sign-in {
  border-color: #2563eb;
  color: #2563eb;
}

.login-demo__sign-in:hover:not(:disabled) {
  background: #eff6ff;
}
</style>
