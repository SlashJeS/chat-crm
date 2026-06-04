<script setup lang="ts">
import { computed, ref } from "vue";

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

const headerTitle = computed(() => {
  if (!props.conversation) {
    return "";
  }
  return props.conversation.fan.display_name;
});

const headerSubtitle = computed(() => {
  if (!props.conversation) {
    return "";
  }
  return props.conversation.model_account.name;
});

const statusClass = computed(() => {
  if (props.connectionState === "connected") {
    return "chat-window__status--connected";
  }
  if (props.connectionState === "reconnecting" || props.connectionState === "connecting") {
    return "chat-window__status--reconnecting";
  }
  if (props.socketError) {
    return "chat-window__status--error";
  }
  return "chat-window__status--disconnected";
});

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
          <h2>{{ headerTitle }}</h2>
          <p class="chat-window__subtitle">{{ headerSubtitle }}</p>
          <div class="chat-window__badges">
            <OverdueBadge :count="conversation.is_overdue ? 1 : 0" />
            <span v-if="conversation.unread_count > 0" class="chat-window__unread">
              {{ conversation.unread_count }} unread
            </span>
          </div>
        </div>
        <div class="chat-window__actions">
          <span class="chat-window__status" :class="statusClass">
            {{ connectionLabel }}
          </span>
          <button type="button" class="chat-window__action" @click="ppvOpen = true">
            Send PPV
          </button>
          <button
            type="button"
            class="chat-window__demo"
            :disabled="simulateLoading"
            title="Dev-only: simulates an incoming fan message via REST"
            @click="handleSimulateFanMessage"
          >
            {{ simulateLoading ? "Simulating…" : "Simulate fan (dev)" }}
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

      <p v-if="simulateError" class="chat-window__error">{{ simulateError }}</p>

      <PPVModal
        :open="ppvOpen"
        :disabled="!isConnected"
        @close="ppvOpen = false"
        @send="handleSendPpv"
      />
    </template>

    <div v-else class="chat-window__placeholder">
      <p>Select a conversation</p>
      <span>Choose a fan dialog from the list to view messages and reply.</span>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.chat-window__header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
}

.chat-window__header-main h2 {
  margin: 0;
  font-size: 1.15rem;
}

.chat-window__subtitle {
  margin: 0.15rem 0 0;
  color: #64748b;
  font-size: 0.85rem;
}

.chat-window__badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.45rem;
}

.chat-window__unread {
  font-size: 0.75rem;
  font-weight: 600;
  color: #2563eb;
}

.chat-window__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.chat-window__status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: #f1f5f9;
}

.chat-window__status--connected {
  color: #15803d;
  background: #dcfce7;
}

.chat-window__status--reconnecting {
  color: #b45309;
  background: #fef3c7;
}

.chat-window__status--disconnected {
  color: #64748b;
}

.chat-window__status--error {
  color: #c0392b;
  background: #fdecea;
}

.chat-window__action {
  padding: 0.4rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  background: #fff;
  cursor: pointer;
  font-size: 0.85rem;
}

.chat-window__demo {
  padding: 0.4rem 0.75rem;
  border: 1px dashed #94a3b8;
  border-radius: 0.375rem;
  background: #f8fafc;
  color: #475569;
  cursor: pointer;
  font-size: 0.8rem;
}

.chat-window__demo:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #64748b;
}

.chat-window__placeholder {
  flex: 1;
  display: grid;
  place-content: center;
  text-align: center;
  color: #64748b;
  padding: 2rem;
}

.chat-window__placeholder p {
  margin: 0 0 0.35rem;
  font-weight: 600;
  color: #475569;
  font-size: 1.05rem;
}

.chat-window__placeholder span {
  font-size: 0.9rem;
}

.chat-window__error {
  margin: 0;
  padding: 0 1rem 0.75rem;
  color: #c0392b;
  font-size: 0.85rem;
}
</style>
