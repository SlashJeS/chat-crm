<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";

import ChatWindow from "@/components/chat/ChatWindow.vue";
import DialogList from "@/components/chat/DialogList.vue";
import AppLayout from "@/components/common/AppLayout.vue";
import ErrorState from "@/components/common/ErrorState.vue";
import LoadingState from "@/components/common/LoadingState.vue";
import { useChatSocket } from "@/composables/useChatSocket";
import { useAuthStore } from "@/stores/auth.store";
import { useConversationsStore } from "@/stores/conversations.store";
import { useMessagesStore } from "@/stores/messages.store";
import type { SendMessagePayload } from "@/types/messages";

const auth = useAuthStore();
const conversationsStore = useConversationsStore();
const messagesStore = useMessagesStore();
const chatSocket = useChatSocket();

let previousConversationId: number | null = null;

const activeMessagesError = computed(() => {
  const id = conversationsStore.activeConversationId;
  if (id === null) {
    return null;
  }
  return messagesStore.errorByConversationId[id] ?? null;
});

async function activateConversation(conversationId: number): Promise<void> {
  conversationsStore.setActiveConversation(conversationId);
  await messagesStore.loadInitialMessages(conversationId);
  chatSocket.subscribeDialog(conversationId);

  const messages = messagesStore.getMessages(conversationId);
  const lastMessageId = messages.filter((message) => message.id > 0).at(-1)?.id;
  if (lastMessageId) {
    await conversationsStore.markConversationRead(conversationId, lastMessageId);
    chatSocket.markRead(conversationId, lastMessageId);
  }
}

async function handleSelectConversation(conversationId: number): Promise<void> {
  if (previousConversationId !== null && previousConversationId !== conversationId) {
    chatSocket.unsubscribeDialog(previousConversationId);
    messagesStore.clearConversation(previousConversationId);
  }
  previousConversationId = conversationId;
  await activateConversation(conversationId);
}

function handleSendMessage(payload: SendMessagePayload): void {
  chatSocket.sendMessage(payload);
}

function handleLoadOlder(): void {
  if (conversationsStore.activeConversationId !== null) {
    messagesStore.loadOlderMessages(conversationsStore.activeConversationId);
  }
}

async function handleRetryMessages(): Promise<void> {
  if (conversationsStore.activeConversationId !== null) {
    await messagesStore.loadInitialMessages(conversationsStore.activeConversationId);
  }
}

async function handleRetryConversations(): Promise<void> {
  await conversationsStore.loadConversations();
}

onMounted(async () => {
  await auth.restoreSession();
  await conversationsStore.loadConversations();
  chatSocket.connect();
});

onUnmounted(() => {
  if (previousConversationId !== null) {
    chatSocket.unsubscribeDialog(previousConversationId);
  }
  chatSocket.disconnect();
  conversationsStore.clear();
  messagesStore.clear();
});

const connectionStatusClass = computed(() => {
  const state = chatSocket.connectionState.value;
  if (state === "connected") {
    return "workspace__connection--connected";
  }
  if (state === "reconnecting" || state === "connecting") {
    return "workspace__connection--reconnecting";
  }
  if (chatSocket.lastError.value) {
    return "workspace__connection--error";
  }
  return "workspace__connection--disconnected";
});
</script>

<template>
  <AppLayout>
    <LoadingState
      v-if="conversationsStore.isLoading"
      message="Loading conversations..."
    />

    <ErrorState
      v-else-if="conversationsStore.error"
      title="Could not load conversations"
      :message="conversationsStore.error"
      retry-label="Retry"
      @retry="handleRetryConversations"
    />

    <div v-else class="workspace">
      <aside class="workspace__sidebar">
        <div class="workspace__connection" :class="connectionStatusClass">
          <span class="workspace__connection-label">{{ chatSocket.connectionLabel.value }}</span>
          <span v-if="chatSocket.lastError.value" class="workspace__connection-error">
            {{ chatSocket.lastError.value }}
          </span>
        </div>
        <DialogList
          :conversations="conversationsStore.conversations"
          :active-conversation-id="conversationsStore.activeConversationId"
          @select="handleSelectConversation"
        />
      </aside>
      <section class="workspace__main">
        <ChatWindow
          :conversation="conversationsStore.activeConversation"
          :messages="
            conversationsStore.activeConversationId
              ? messagesStore.getMessages(conversationsStore.activeConversationId)
              : []
          "
          :has-more="
            conversationsStore.activeConversationId
              ? messagesStore.hasMoreByConversationId[conversationsStore.activeConversationId] ?? false
              : false
          "
          :loading-messages="
            conversationsStore.activeConversationId
              ? messagesStore.loadingByConversationId[conversationsStore.activeConversationId] ?? false
              : false
          "
          :messages-error="activeMessagesError"
          :is-connected="chatSocket.isConnected.value"
          :connection-label="chatSocket.connectionLabel.value"
          :connection-state="chatSocket.connectionState.value"
          :socket-error="chatSocket.lastError.value"
          @send-message="handleSendMessage"
          @load-older="handleLoadOlder"
          @retry-messages="handleRetryMessages"
        />
      </section>
    </div>
  </AppLayout>
</template>

<style scoped>
.workspace {
  display: grid;
  grid-template-columns: 320px 1fr;
  height: calc(100vh - 65px);
  margin: -1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #fff;
}

.workspace__sidebar,
.workspace__main {
  min-height: 0;
}

.workspace__sidebar {
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e2e8f0;
}

.workspace__connection {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.65rem 1rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  flex-shrink: 0;
}

.workspace__connection-label {
  font-weight: 600;
}

.workspace__connection--connected .workspace__connection-label {
  color: #15803d;
}

.workspace__connection--reconnecting .workspace__connection-label {
  color: #b45309;
}

.workspace__connection--disconnected .workspace__connection-label {
  color: #64748b;
}

.workspace__connection--error .workspace__connection-label {
  color: #c0392b;
}

.workspace__connection-error {
  font-size: 0.8rem;
  color: #c0392b;
}
</style>
