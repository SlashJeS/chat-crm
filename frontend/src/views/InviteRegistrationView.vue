<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import AppLogo from "@/components/common/AppLogo.vue";
import ErrorState from "@/components/common/ErrorState.vue";
import LoadingState from "@/components/common/LoadingState.vue";
import ThemeToggle from "@/components/common/ThemeToggle.vue";
import { publicInviteAccept, publicInviteDetail } from "@/api/endpoints";
import { http } from "@/api/http";
import { useAuthStore } from "@/stores/auth.store";
import type { AcceptInvitePayload, AcceptInviteResponse, PublicInvite } from "@/types/admin";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const invite = ref<PublicInvite | null>(null);
const isLoading = ref(true);
const loadError = ref<string | null>(null);
const isSubmitting = ref(false);
const submitError = ref<string | null>(null);
const isSuccess = ref(false);

const username = ref("");
const displayName = ref("");
const email = ref("");
const password = ref("");
const passwordConfirm = ref("");

const token = computed(() => String(route.params.token ?? ""));

const isActive = computed(() => invite.value?.is_active_invite === true);

const roleLabel = computed(() => {
  const role = invite.value?.role;
  if (role === "TEAMLEAD") {
    return "Teamlead";
  }
  return "Chatter";
});

const emailReadOnly = computed(() => Boolean(invite.value?.email));

const statusMessage = computed(() => {
  if (!invite.value) {
    return "";
  }
  switch (invite.value.status) {
    case "accepted":
      return "This invite has already been used.";
    case "revoked":
      return "This invite was revoked.";
    case "expired":
      return "This invite has expired.";
    default:
      return "This invite is no longer available.";
  }
});

async function loadInvite(): Promise<void> {
  isLoading.value = true;
  loadError.value = null;
  try {
    const { data } = await http.get<PublicInvite>(publicInviteDetail(token.value));
    invite.value = data;
    if (data.email) {
      email.value = data.email;
    }
  } catch {
    loadError.value = "Invite not found or unavailable.";
  } finally {
    isLoading.value = false;
  }
}

function parseSubmitErrors(error: unknown): void {
  submitError.value = "Registration failed. Please check the form and try again.";
  if (typeof error === "object" && error !== null && "response" in error) {
    const response = (error as { response?: { data?: Record<string, unknown> } }).response;
    const data = response?.data;
    if (data && typeof data.detail === "string") {
      submitError.value = data.detail;
    } else if (data) {
      const messages = Object.values(data)
        .flatMap((value) => (Array.isArray(value) ? value : [String(value)]))
        .filter(Boolean);
      if (messages.length) {
        submitError.value = messages.join(" ");
      }
    }
  }
}

async function handleSubmit(): Promise<void> {
  if (!invite.value || !isActive.value) {
    return;
  }

  submitError.value = null;

  if (password.value !== passwordConfirm.value) {
    submitError.value = "Passwords do not match.";
    return;
  }

  isSubmitting.value = true;
  try {
    const payload: AcceptInvitePayload = {
      username: username.value.trim(),
      password: password.value,
      password_confirm: passwordConfirm.value,
    };
    const trimmedDisplayName = displayName.value.trim();
    if (trimmedDisplayName) {
      payload.display_name = trimmedDisplayName;
    }
    if (!emailReadOnly.value) {
      payload.email = email.value.trim();
    } else if (email.value.trim()) {
      payload.email = email.value.trim();
    }

    await http.post<AcceptInviteResponse>(publicInviteAccept(token.value), payload);
    isSuccess.value = true;
  } catch (error) {
    parseSubmitErrors(error);
  } finally {
    isSubmitting.value = false;
  }
}

function goToLogin(): void {
  router.push("/login");
}

function logoutFirst(): void {
  auth.logout();
}

onMounted(() => {
  loadInvite();
});
</script>

<template>
  <div class="invite-page">
    <div class="invite-page__toolbar">
      <ThemeToggle compact />
    </div>

    <div class="invite-page__shell">
      <div class="invite-page__card card">
        <header class="invite-page__header">
          <AppLogo variant="full" size="md" />
          <h1 class="invite-page__title">Create your account</h1>
          <p v-if="invite && isActive" class="invite-page__subtitle muted">
            You are joining as {{ roleLabel }}
          </p>
        </header>

        <LoadingState v-if="isLoading" message="Loading invite…" size="md" />

        <ErrorState
          v-else-if="loadError"
          title="Invite unavailable"
          :message="loadError"
        />

        <div v-else-if="isSuccess" class="invite-page__success">
          <p class="invite-page__success-title">Account created</p>
          <p class="invite-page__success-text muted">
            Your account was created successfully. Sign in with the password you chose.
          </p>
          <button type="button" class="btn btn-primary" @click="goToLogin">Go to login</button>
        </div>

        <div v-else-if="!isActive" class="invite-page__inactive">
          <p class="invite-page__inactive-title">{{ statusMessage }}</p>
          <p class="muted">Contact your administrator if you need a new invite link.</p>
        </div>

        <div v-else-if="auth.isAuthenticated" class="invite-page__logged-in">
          <p class="invite-page__logged-in-title">
            You are currently logged in as {{ auth.user?.display_name }}.
          </p>
          <p class="muted">Log out before accepting an invite with a different account.</p>
          <button type="button" class="btn btn-secondary" @click="logoutFirst">Log out</button>
        </div>

        <form v-else class="invite-page__form" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label" for="invite-username">Username</label>
            <input
              id="invite-username"
              v-model="username"
              class="input"
              type="text"
              autocomplete="username"
              required
              :disabled="isSubmitting"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="invite-display-name">Display name</label>
            <input
              id="invite-display-name"
              v-model="displayName"
              class="input"
              type="text"
              autocomplete="name"
              placeholder="Optional"
              :disabled="isSubmitting"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="invite-email">Email</label>
            <input
              id="invite-email"
              v-model="email"
              class="input"
              type="email"
              autocomplete="email"
              :readonly="emailReadOnly"
              :required="!emailReadOnly"
              :disabled="isSubmitting || emailReadOnly"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="invite-password">Password</label>
            <input
              id="invite-password"
              v-model="password"
              class="input"
              type="password"
              autocomplete="new-password"
              required
              :disabled="isSubmitting"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="invite-password-confirm">Confirm password</label>
            <input
              id="invite-password-confirm"
              v-model="passwordConfirm"
              class="input"
              type="password"
              autocomplete="new-password"
              required
              :disabled="isSubmitting"
            />
          </div>

          <p v-if="submitError" class="invite-page__error" role="alert">{{ submitError }}</p>

          <button type="submit" class="btn btn-primary invite-page__submit" :disabled="isSubmitting">
            {{ isSubmitting ? "Creating account…" : "Create account" }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.invite-page {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  background: var(--color-bg);
}

.invite-page__toolbar {
  position: fixed;
  top: var(--space-4);
  right: var(--space-4);
  z-index: 20;
}

.invite-page__shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: calc(var(--space-8) + 1rem) var(--space-4) var(--space-8);
}

.invite-page__card {
  width: min(100%, 26rem);
  padding: var(--space-5);
  box-shadow: var(--shadow-md);
}

.invite-page__header {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
}

.invite-page__title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.invite-page__subtitle {
  margin: 0;
  font-size: 0.875rem;
}

.invite-page__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.invite-page__submit {
  margin-top: var(--space-3);
  width: 100%;
}

.invite-page__error {
  margin: var(--space-2) 0 0;
  color: var(--color-danger);
  font-size: 0.8125rem;
}

.invite-page__success,
.invite-page__inactive,
.invite-page__logged-in {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.invite-page__success-title,
.invite-page__inactive-title,
.invite-page__logged-in-title {
  margin: 0;
  font-weight: 600;
  color: var(--color-text);
}
</style>
