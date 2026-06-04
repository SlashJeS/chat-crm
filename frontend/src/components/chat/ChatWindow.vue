<script setup lang="ts">
import { computed, ref } from "vue";

import AppLogo from "@/components/common/AppLogo.vue";
import MessageInput from "@/components/chat/MessageInput.vue";
import MessageList from "@/components/chat/MessageList.vue";
import PPVModal from "@/components/chat/PPVModal.vue";
import OverdueBadge from "@/components/monitor/OverdueBadge.vue";
import { DEV_SIMULATE_FAN_MESSAGE } from "@/api/endpoints";
import { http } from "@/api/http";
import { useAuthStore } from "@/stores/auth.store";
import { useMessagesStore } from "@/stores/messages.store";
import type { Conversation } from "@/types/conversations";
import type { Message, SendMessagePayload } from "@/types/messages";
import { getInitials } from "@/utils/initials";
import { getConnectionTone, getRealtimeConnectionLabel } from "@/utils/status";
import type { ConnectionState } from "@/websocket/socket";

const props = defineProps<{
  conversation: Conversation | null;
  messages: Message[];
  hasMore: boolean;
  loadingMessages: boolean;
  messagesError?: string | null;
  isConnected: boolean;
  connectionLabel: string;
  connectionState: ConnectionState;
  socketError: string | null;
}>();

const emit = defineEmits<{
  sendMessage: [payload: SendMessagePayload];
  loadOlder: [];
  retryMessages: [];
  simulateFanMessage: [];
}>();

const auth = useAuthStore();
const messagesStore = useMessagesStore();
const ppvOpen = ref(false);
const simulateError = ref<string | null>(null);
const simulateLoading = ref(false);

const fanInitials = computed(() =>
  props.conversation ? getInitials(props.conversation.fan.display_name) : "",
);

const isWaiting = computed(
  () => props.conversation?.waiting_since !== null && props.conversation?.waiting_since !== undefined,
);

const statusClass = computed(() =>
  `status-pill--${getConnectionTone(props.connectionState, Boolean(props.socketError))}`,
);

const realtimeLabel = computed(() => getRealtimeConnectionLabel(props.connectionState));

function buildPendingMessage(
  text: string,
  messageType: "TEXT" | "PPV",
  ppvPrice: string | null,
): { payload: SendMessagePayload; pending: Message } {
  const clientMessageId = crypto.randomUUID();
  const conversationId = props.conversation!.id;
  const payload: SendMessagePayload = {
    type: "message.send",
    conversation_id: conversationId,
    message_type: messageType,
    text,
    ppv_price: messageType === "PPV" ? ppvPrice : null,
    client_message_id: clientMessageId,
  };
  const pending: Message = {
    id: -Date.now(),
    conversation: conversationId,
    sender_type: "CHATTER",
    sender_user: auth.user
      ? {
          id: auth.user.id,
          username: auth.user.username,
          display_name: auth.user.display_name,
        }
      : null,
    message_type: messageType,
    text,
    ppv_price: messageType === "PPV" ? ppvPrice : null,
    client_message_id: clientMessageId,
    created_at: new Date().toISOString(),
    local_status: "pending",
  };
  return { payload, pending };
}

function handleSendText(text: string): void {
  if (!props.conversation) {
    return;
  }
  const { payload, pending } = buildPendingMessage(text, "TEXT", null);
  messagesStore.addPendingMessage(props.conversation.id, pending);
  emit("sendMessage", payload);
}

function handleSendPpv(payload: { text: string; ppvPrice: string }): void {
  if (!props.conversation) {
    return;
  }
  const { payload: wsPayload, pending } = buildPendingMessage(
    payload.text,
    "PPV",
    payload.ppvPrice,
  );
  messagesStore.addPendingMessage(props.conversation.id, pending);
  emit("sendMessage", wsPayload);
}

async function handleSimulateFanMessage(): Promise<void> {
  if (!props.conversation) {
    return;
  }
  simulateLoading.value = true;
  simulateError.value = null;
  try {
    await http.post(DEV_SIMULATE_FAN_MESSAGE, {
      conversation_id: props.conversation.id,
      text: "Hello from simulated fan",
    });
    emit("simulateFanMessage");
  } catch {
    simulateError.value = "Failed to simulate fan message";
  } finally {
    simulateLoading.value = false;
  }
}
</script>

<template>
  <div class="chat-window">
    <template v-if="conversation">
      <header class="chat-window__header">
        <div class="chat-window__header-main">
          <span class="avatar avatar--lg chat-window__avatar">{{ fanInitials }}</span>
          <div class="chat-window__header-text">
            <h2>{{ conversation.fan.display_name }}</h2>
            <p class="chat-window__subtitle">{{ conversation.model_account.name }}</p>
            <div class="chat-window__badges">
              <OverdueBadge v-if="conversation.is_overdue" :count="1" />
              <span v-if="isWaiting && !conversation.is_overdue" class="badge badge-warning">
                Waiting
              </span>
              <span v-if="conversation.unread_count > 0" class="badge badge-success">
                {{ conversation.unread_count }} unread
              </span>
              <span class="status-pill chat-window__status" :class="statusClass">
                <span class="status-dot" aria-hidden="true" />
                {{ realtimeLabel }}
              </span>
            </div>
          </div>
        </div>
        <div class="chat-window__actions">
          <button
            type="button"
            class="btn btn-secondary"
            aria-label="Send paid PPV message"
            @click="ppvOpen = true"
          >
            Send PPV
          </button>
          <button
            type="button"
            class="chat-window__demo"
            :disabled="simulateLoading"
            aria-label="Simulate incoming fan message for demo"
            title="Dev-only: simulates an incoming fan message via REST"
            @click="handleSimulateFanMessage"
          >
            <span class="chat-window__demo-tag">Demo</span>
            {{ simulateLoading ? "Simulating…" : "Simulate fan message" }}
          </button>
        </div>
      </header>

      <MessageList
        :messages="messages"
        :has-more="hasMore"
        :loading="loadingMessages"
        :error="messagesError"
        @load-older="emit('loadOlder')"
        @retry="emit('retryMessages')"
      />

      <MessageInput
        :disabled="!isConnected"
        :socket-error="socketError"
        @send="handleSendText"
      />

      <p v-if="simulateError" class="chat-window__error" role="alert">{{ simulateError }}</p>

      <PPVModal
        :open="ppvOpen"
        :disabled="!isConnected"
        @close="ppvOpen = false"
        @send="handleSendPpv"
      />
    </template>

    <div v-else class="chat-window__placeholder">
      <div class="chat-window__placeholder-card card empty-state">
        <div class="empty-state__icon">
          <AppLogo variant="mark" size="sm" />
        </div>
        <h2 class="empty-state__title">Select a dialog</h2>
        <p class="empty-state__text">
          Choose a fan dialog from the sidebar to view messages and reply in realtime.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  background: var(--color-surface);
}

.chat-window__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  flex: 0 0 auto;
}

.chat-window__header-main {
  display: flex;
  gap: var(--space-3);
  min-width: 0;
  flex: 1;
}

.chat-window__avatar {
  flex-shrink: 0;
}

.chat-window__header-text {
  min-width: 0;
}

.chat-window__header-text h2 {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text);
}

.chat-window__subtitle {
  margin: var(--space-1) 0 0;
  color: var(--color-text-muted);
  font-size: 0.82rem;
}

.chat-window__badges {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
  flex-wrap: wrap;
}

.chat-window__status {
  font-size: 0.72rem;
}

.chat-window__actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
  justify-content: flex-end;
  flex-shrink: 0;
}

.chat-window__demo {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0.35rem 0.6rem;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 500;
}

.chat-window__demo:hover:not(:disabled) {
  background: var(--color-surface-hover);
  border-color: var(--color-warning);
  color: var(--color-text);
}

.chat-window__demo:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chat-window__demo-tag {
  padding: 0.1rem 0.35rem;
  border-radius: var(--radius-sm);
  background: var(--color-warning-soft);
  color: var(--color-warning);
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.chat-window__placeholder {
  flex: 1 1 auto;
  min-height: 0;
  display: grid;
  place-items: center;
  padding: var(--space-4);
  overflow: hidden;
}

.chat-window__placeholder-card {
  max-width: 22rem;
  padding: var(--space-5);
}

.chat-window__error {
  margin: 0;
  padding: 0 var(--space-4) var(--space-3);
  color: var(--color-danger);
  font-size: 0.85rem;
}

@media (max-width: 640px) {
  .chat-window__header {
    flex-direction: column;
  }

  .chat-window__actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
