<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import AppLogo from "@/components/common/AppLogo.vue";
import LoadingState from "@/components/common/LoadingState.vue";
import ThemeToggle from "@/components/common/ThemeToggle.vue";
import { isPathAllowedForRole } from "@/router/index";
import { useAuthStore } from "@/stores/auth.store";
import type { UserRole } from "@/types/auth";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const username = ref("");
const password = ref("");

const features = [
  "Live WebSocket chat",
  "SLA response tracking",
  "Teamlead workload monitor",
];

const demoAccounts = [
  { label: "Teamlead", username: "lead", password: "password123", role: "TEAMLEAD" as UserRole },
  { label: "Chatter One", username: "chatter1", password: "password123", role: "CHATTER" as UserRole },
  { label: "Chatter Two", username: "chatter2", password: "password123", role: "CHATTER" as UserRole },
  { label: "Chatter Three", username: "chatter3", password: "password123", role: "CHATTER" as UserRole },
];

function redirectAfterLogin(role: UserRole): void {
  const redirect =
    typeof route.query.redirect === "string" && route.query.redirect.startsWith("/")
      ? route.query.redirect
      : null;

  if (redirect && isPathAllowedForRole(redirect, role)) {
    router.replace(redirect);
    return;
  }

  if (role === "CHATTER") {
    router.replace("/chatter");
    return;
  }
  router.replace("/teamlead");
}

async function handleSubmit(): Promise<void> {
  try {
    const loadedUser = await auth.login(username.value, password.value);
    redirectAfterLogin(loadedUser.role);
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
    <div class="login-page__toolbar">
      <ThemeToggle />
    </div>

    <div class="login-page__shell">
      <div class="login-page__card card">
        <aside class="login-page__hero">
          <div class="login-page__hero-content">
            <AppLogo variant="full" size="lg" />
            <p class="login-page__product">CRM Chatters</p>
            <h1 class="login-page__headline">Realtime CRM for chat operations</h1>
            <p class="login-page__description">
              Manage fan dialogs, track chatter presence, and monitor SLA performance from one
              realtime workspace built for chatters and teamleads.
            </p>
            <div class="login-page__features">
              <span v-for="feature in features" :key="feature" class="feature-pill">
                {{ feature }}
              </span>
            </div>
          </div>
        </aside>

        <section class="login-page__form-panel">
          <header class="login-page__form-header">
            <h2 class="login-page__form-title">Sign in</h2>
            <p class="login-page__form-subtitle muted">Use your demo account to explore the product.</p>
          </header>

          <LoadingState v-if="auth.isLoading" message="Signing in…" size="md" />

          <form v-else class="login-form" @submit.prevent="handleSubmit">
            <div class="form-group">
              <label class="form-label" for="login-username">Username</label>
              <input
                id="login-username"
                v-model="username"
                class="input"
                type="text"
                autocomplete="username"
                placeholder="e.g. chatter1"
                required
                :disabled="auth.isLoading"
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="login-password">Password</label>
              <input
                id="login-password"
                v-model="password"
                class="input"
                type="password"
                autocomplete="current-password"
                placeholder="password123"
                required
                :disabled="auth.isLoading"
              />
            </div>

            <p v-if="auth.error" class="form-error" role="alert">{{ auth.error }}</p>

            <button type="submit" class="btn btn-primary login-form__submit" :disabled="auth.isLoading">
              Sign in
            </button>
          </form>

          <hr class="divider" />

          <section class="login-demo">
            <h3 class="login-demo__title">Demo accounts</h3>
            <p class="form-help">All demo passwords are <code>password123</code></p>
            <ul class="login-demo__list">
              <li v-for="account in demoAccounts" :key="account.username" class="login-demo__item">
                <div class="login-demo__account">
                  <strong>{{ account.label }}</strong>
                  <span class="muted">{{ account.username }}</span>
                </div>
                <div class="login-demo__actions">
                  <button
                    type="button"
                    class="btn btn-ghost"
                    :disabled="auth.isLoading"
                    :aria-label="`Fill credentials for ${account.label}`"
                    @click="fillDemo(account)"
                  >
                    Fill
                  </button>
                  <button
                    type="button"
                    class="btn btn-secondary"
                    :disabled="auth.isLoading"
                    :aria-label="`Sign in as ${account.label}`"
                    @click="loginAsDemo(account)"
                  >
                    Sign in
                  </button>
                </div>
              </li>
            </ul>
          </section>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

.login-page__toolbar {
  position: fixed;
  top: var(--space-4);
  right: var(--space-4);
  z-index: 20;
}

.login-page__shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: calc(var(--space-8) + 1rem) var(--space-4) var(--space-8);
}

.login-page__card {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(300px, 400px);
  width: min(880px, 100%);
  overflow: hidden;
  padding: 0;
  box-shadow: var(--shadow-md);
}

.login-page__hero {
  padding: var(--space-6);
  background: var(--color-bg-soft);
  border-right: 1px solid var(--color-border);
}

.login-page__hero-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.login-page__product {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.login-page__headline {
  margin: 0;
  font-size: clamp(1.25rem, 2vw, 1.5rem);
  line-height: 1.25;
  font-weight: 600;
  color: var(--color-text);
}

.login-page__description {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.55;
  font-size: 0.875rem;
}

.login-page__features {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-2);
  margin-top: var(--space-1);
}

.login-page__form-panel {
  padding: var(--space-6);
  background: var(--color-surface);
}

.login-page__form-header {
  margin-bottom: var(--space-4);
}

.login-page__form-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
}

.login-page__form-subtitle {
  margin: var(--space-2) 0 0;
  font-size: 0.875rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.login-form__submit {
  width: 100%;
  margin-top: var(--space-1);
  padding-block: 0.75rem;
}

.login-demo__title {
  margin: 0 0 var(--space-2);
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-text);
}

.login-demo__list {
  list-style: none;
  margin: var(--space-4) 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.login-demo__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-soft);
}

.login-demo__account {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.85rem;
  min-width: 0;
}

.login-demo__account strong {
  color: var(--color-text);
}

.login-demo code {
  padding: 0.1rem 0.35rem;
  border-radius: var(--radius-sm);
  background: var(--color-bg-soft);
  font-size: 0.85rem;
}

.login-demo__actions {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
}

@media (max-width: 860px) {
  .login-page__card {
    grid-template-columns: 1fr;
    max-width: 480px;
  }

  .login-page__hero {
    border-right: none;
    border-bottom: 1px solid var(--color-border-strong);
    padding: var(--space-6);
  }

  .login-page__features {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 520px) {
  .login-demo__item {
    flex-direction: column;
    align-items: stretch;
  }

  .login-demo__actions {
    width: 100%;
  }

  .login-demo__actions .btn {
    flex: 1;
  }
}
</style>
