<script setup lang="ts">
import { computed, ref, watch } from "vue";

import AppIcon from "@/components/common/AppIcon.vue";
import type { CreateInvitePayload, InviteRole, UserInvite } from "@/types/admin";

const props = defineProps<{
  open: boolean;
  isSubmitting?: boolean;
  createdInvite?: UserInvite | null;
}>();

const emit = defineEmits<{
  close: [];
  create: [payload: CreateInvitePayload];
}>();

const role = ref<InviteRole>("CHATTER");
const email = ref("");
const expiryHours = ref(72);
const copyFeedback = ref("");

const expiryOptions = [
  { label: "24 hours", value: 24 },
  { label: "72 hours", value: 72 },
  { label: "7 days", value: 168 },
];

const isSuccess = computed(() => Boolean(props.createdInvite));

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen && !props.createdInvite) {
      role.value = "CHATTER";
      email.value = "";
      expiryHours.value = 72;
      copyFeedback.value = "";
    }
  },
);

function handleSubmit(): void {
  const payload: CreateInvitePayload = {
    role: role.value,
    expires_in_hours: expiryHours.value,
  };
  const trimmedEmail = email.value.trim();
  if (trimmedEmail) {
    payload.email = trimmedEmail;
  }
  emit("create", payload);
}

async function copyLink(): Promise<void> {
  if (!props.createdInvite?.invite_url) {
    return;
  }
  try {
    await navigator.clipboard.writeText(props.createdInvite.invite_url);
    copyFeedback.value = "Copied";
  } catch {
    copyFeedback.value = "Copy failed";
  }
}
</script>

<template>
  <div v-if="open" class="invite-modal">
    <div class="invite-modal__backdrop" aria-hidden="true" @click="emit('close')" />
    <div
      class="invite-modal__panel panel"
      role="dialog"
      aria-modal="true"
      aria-labelledby="invite-modal-title"
    >
      <header class="invite-modal__header">
        <h3 id="invite-modal-title" class="invite-modal__title">
          {{ isSuccess ? "Invite link ready" : "Add user" }}
        </h3>
        <button type="button" class="invite-modal__close" aria-label="Close" @click="emit('close')">
          <AppIcon name="close" size="sm" />
        </button>
      </header>

      <template v-if="isSuccess && createdInvite">
        <p class="invite-modal__hint muted">
          Send this link to the new {{ createdInvite.role === "TEAMLEAD" ? "teamlead" : "chatter" }}.
          They will choose their own username and password when registering.
        </p>
        <div class="invite-modal__link-row">
          <input
            class="input invite-modal__link-input"
            type="text"
            readonly
            :value="createdInvite.invite_url"
            aria-label="Invite link"
          />
          <button type="button" class="btn btn-secondary" @click="copyLink">
            {{ copyFeedback || "Copy link" }}
          </button>
        </div>
        <div class="invite-modal__meta muted">
          <span>Role: {{ createdInvite.role }}</span>
          <span v-if="createdInvite.email">Email: {{ createdInvite.email }}</span>
        </div>
        <footer class="invite-modal__footer">
          <button type="button" class="btn btn-primary" @click="emit('close')">Done</button>
        </footer>
      </template>

      <form v-else class="invite-modal__form" @submit.prevent="handleSubmit">
        <p class="invite-modal__hint muted">
          Create an invite link. The recipient registers with their own credentials.
        </p>

        <div class="form-group">
          <label class="form-label" for="invite-role">Role</label>
          <select id="invite-role" v-model="role" class="input">
            <option value="CHATTER">Chatter</option>
            <option value="TEAMLEAD">Teamlead</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label" for="invite-email">Email (optional)</label>
          <input
            id="invite-email"
            v-model="email"
            class="input"
            type="email"
            autocomplete="off"
            placeholder="Lock invite to a specific email"
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="invite-expiry">Expires in</label>
          <select id="invite-expiry" v-model.number="expiryHours" class="input">
            <option v-for="option in expiryOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <footer class="invite-modal__footer">
          <button type="button" class="btn btn-secondary" @click="emit('close')">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? "Creating…" : "Create invite" }}
          </button>
        </footer>
      </form>
    </div>
  </div>
</template>

<style scoped>
.invite-modal {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}

.invite-modal__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
}

.invite-modal__panel {
  position: relative;
  z-index: 1;
  width: min(100%, 28rem);
  padding: var(--space-4);
}

.invite-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.invite-modal__title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.invite-modal__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-soft);
  color: var(--color-text-muted);
  cursor: pointer;
}

.invite-modal__hint {
  margin: 0 0 var(--space-4);
  font-size: 0.8125rem;
  line-height: 1.45;
}

.invite-modal__form {
  display: flex;
  flex-direction: column;
}

.invite-modal__link-row {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.invite-modal__link-input {
  flex: 1;
  min-width: 0;
  font-size: 0.8125rem;
}

.invite-modal__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  font-size: 0.75rem;
  margin-bottom: var(--space-4);
}

.invite-modal__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-2);
}
</style>
