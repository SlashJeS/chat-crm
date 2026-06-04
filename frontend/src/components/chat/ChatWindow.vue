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

const props = defineProps<{
  conversation: Conversation | null;
  messages: Message[];
  hasMore: boolean;
  loadingMessages: boolean;
  isConnected: boolean;
  socketError: string | null;
}>();

const emit = defineEmits<{
  sendMessage: [payload: SendMessagePayload];
  loadOlder: [];
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
  return `${props.conversation.fan.display_name} · ${props.conversation.model_account.name}`;
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
  ppvOpen.value = false;
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
        <div>
          <h2>{{ headerTitle }}</h2>
          <OverdueBadge :overdue="conversation.is_overdue" />
        </div>
        <div class="chat-window__actions">
          <span class="chat-window__status" :class="{ 'chat-window__status--online': isConnected }">
            {{ isConnected ? "Live" : "Offline" }}
          </span>
          <button type="button" @click="ppvOpen = true">Send PPV</button>
          <button
            type="button"
            :disabled="simulateLoading"
            @click="handleSimulateFanMessage"
          >
            Simulate fan message
          </button>
        </div>
      </header>

      <MessageList
        :messages="messages"
        :has-more="hasMore"
        :loading="loadingMessages"
        @load-older="emit('loadOlder')"
      />

      <MessageInput
        :disabled="!isConnected"
        :socket-error="socketError"
        @send="handleSendText"
      />

      <p v-if="simulateError" class="chat-window__error">{{ simulateError }}</p>

      <PPVModal :open="ppvOpen" @close="ppvOpen = false" @send="handleSendPpv" />
    </template>

    <div v-else class="chat-window__placeholder">Select a conversation</div>
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
  padding: 1rem;
  border-bottom: 1px solid #ddd;
}

.chat-window__header h2 {
  margin: 0 0 0.35rem;
  font-size: 1.1rem;
}

.chat-window__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.chat-window__status {
  font-size: 0.85rem;
  color: #666;
}

.chat-window__status--online {
  color: #15803d;
}

.chat-window__placeholder {
  flex: 1;
  display: grid;
  place-items: center;
  color: #666;
}

.chat-window__error {
  margin: 0;
  padding: 0 1rem 0.75rem;
  color: #c0392b;
  font-size: 0.85rem;
}
</style>
