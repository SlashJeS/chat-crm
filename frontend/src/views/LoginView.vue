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
  "Live chat and WebSockets",
  "Response SLA tracking",
  "Teamlead workload monitor",
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
</script>

<template>
  <div class="login-page">
    <div class="login-page__toolbar">
      <ThemeToggle />
    </div>

    <div class="login-page__shell">
      <div class="login-page__card">
        <aside class="login-page__hero">
          <div class="login-page__hero-inner">
            <AppLogo variant="full" size="lg" />
            <p class="login-page__eyebrow">CRM Chatters</p>
            <h1 class="login-page__headline">Realtime CRM for chat operations</h1>
            <p class="login-page__description">
              Manage fan dialogs, track chatter presence, and monitor response SLA in one focused
              workspace for chatters and teamleads.
            </p>
            <ul class="login-page__features" aria-label="Product features">
              <li v-for="feature in features" :key="feature" class="login-page__feature">
                {{ feature }}
              </li>
            </ul>
          </div>
        </aside>

        <section class="login-page__form-panel">
          <div class="login-page__form-inner">
            <header class="login-page__form-header">
              <h2 class="login-page__form-title">Sign in</h2>
              <p class="login-page__form-subtitle">Sign in to access your workspace.</p>
            </header>

            <LoadingState v-if="auth.isLoading" message="Signing in…" size="md" />

            <form v-else class="login-form" @submit.prevent="handleSubmit">
              <div class="login-form__group">
                <label class="login-form__label" for="login-username">Username</label>
                <input
                  id="login-username"
                  v-model="username"
                  class="login-form__input"
                  type="text"
                  autocomplete="username"
                  placeholder="Enter your username"
                  required
                  :disabled="auth.isLoading"
                />
              </div>

              <div class="login-form__group">
                <label class="login-form__label" for="login-password">Password</label>
                <input
                  id="login-password"
                  v-model="password"
                  class="login-form__input"
                  type="password"
                  autocomplete="current-password"
                  placeholder="Enter your password"
                  required
                  :disabled="auth.isLoading"
                />
              </div>

              <p v-if="auth.error" class="login-form__error" role="alert">{{ auth.error }}</p>

              <button
                type="submit"
                class="login-form__submit"
                :disabled="auth.isLoading"
              >
                Sign in
              </button>

              <p class="login-form__footnote">
                Use the credentials provided by your administrator.
              </p>
            </form>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  background: var(--color-bg);
}

.login-page__toolbar {
  position: fixed;
  top: var(--space-5);
  right: var(--space-5);
  z-index: 20;
}

.login-page__shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: calc(var(--space-8) + 2rem) var(--space-5) var(--space-8);
}

.login-page__card {
  display: grid;
  grid-template-columns: minmax(300px, 1.05fr) minmax(320px, 420px);
  width: min(920px, 100%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--color-surface);
  box-shadow: var(--shadow-lg);
}

.login-page__hero {
  padding: var(--space-8);
  background: var(--color-bg-soft);
  border-right: 1px solid var(--color-border);
  display: flex;
  align-items: center;
}

.login-page__hero-inner {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-width: 26rem;
}

.login-page__eyebrow {
  margin: 0;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-soft);
}

.login-page__headline {
  margin: 0;
  font-size: clamp(1.375rem, 2.2vw, 1.75rem);
  line-height: 1.2;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.login-page__description {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.6;
  font-size: 0.9375rem;
}

.login-page__features {
  list-style: none;
  margin: var(--space-2) 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.login-page__feature {
  position: relative;
  padding-left: 1.125rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}

.login-page__feature::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.45em;
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
  background: var(--color-primary);
  opacity: 0.85;
}

.login-page__form-panel {
  padding: var(--space-8);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
}

.login-page__form-inner {
  width: 100%;
  max-width: 22rem;
}

.login-page__form-header {
  margin-bottom: var(--space-6);
}

.login-page__form-title {
  margin: 0;
  font-size: 1.375rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.login-page__form-subtitle {
  margin: var(--space-2) 0 0;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.login-form__group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.login-form__label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: 0.01em;
}

.login-form__input {
  width: 100%;
  height: 2.875rem;
  padding: 0 0.875rem;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-bg-soft);
  color: var(--color-text);
  font: inherit;
  font-size: 0.9375rem;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    background-color var(--transition-fast);
}

.login-form__input::placeholder {
  color: var(--color-text-soft);
}

.login-form__input:hover:not(:disabled) {
  border-color: var(--color-border-strong);
  background: var(--color-surface-raised);
}

.login-form__input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: var(--color-surface);
  box-shadow: 0 0 0 3px var(--color-primary-soft);
}

.login-form__input:focus-visible {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-soft);
}

.login-form__input:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.login-form__error {
  margin: 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--color-danger-soft);
  color: var(--color-danger);
  font-size: 0.875rem;
  line-height: 1.45;
}

.login-form__submit {
  width: 100%;
  height: 2.875rem;
  margin-top: var(--space-1);
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: var(--color-on-primary);
  font: inherit;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    background-color var(--transition-fast),
    transform var(--transition-fast),
    box-shadow var(--transition-fast);
}

.login-form__submit:hover:not(:disabled) {
  background: var(--color-primary-hover);
  box-shadow: var(--shadow-sm);
}

.login-form__submit:active:not(:disabled) {
  transform: translateY(1px);
}

.login-form__submit:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-primary-soft);
}

.login-form__submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.login-form__footnote {
  margin: 0;
  text-align: center;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--color-text-soft);
}

@media (max-width: 860px) {
  .login-page__card {
    grid-template-columns: 1fr;
    max-width: 28rem;
  }

  .login-page__hero {
    border-right: none;
    border-bottom: 1px solid var(--color-border);
    padding: var(--space-6);
  }

  .login-page__hero-inner {
    max-width: none;
  }

  .login-page__form-panel {
    padding: var(--space-6);
  }

  .login-page__form-inner {
    max-width: none;
  }
}

@media (max-width: 480px) {
  .login-page__shell {
    padding: calc(var(--space-8) + 1.5rem) var(--space-4) var(--space-6);
  }

  .login-page__toolbar {
    top: var(--space-4);
    right: var(--space-4);
  }

  .login-page__hero,
  .login-page__form-panel {
    padding: var(--space-5);
  }

  .login-page__headline {
    font-size: 1.25rem;
  }
}
</style>
