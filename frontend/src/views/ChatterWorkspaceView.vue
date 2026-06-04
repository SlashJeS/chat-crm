<script setup lang="ts">
import { onMounted, onUnmounted, watch } from "vue";

import ChatWindow from "@/components/chat/ChatWindow.vue";
import DialogList from "@/components/chat/DialogList.vue";
import AppLayout from "@/components/common/AppLayout.vue";
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

async function activateConversation(conversationId: number): Promise<void> {
  conversationsStore.setActiveConversation(conversationId);
  await messagesStore.loadInitialMessages(conversationId);
  chatSocket.subscribeDialog(conversationId);

  const messages = messagesStore.getMessages(conversationId);
  const lastMessageId = messages.at(-1)?.id;
  await conversationsStore.markConversationRead(conversationId, lastMessageId);
  chatSocket.markRead(conversationId, lastMessageId);
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

watch(
  () => chatSocket.isConnected.value,
  (connected) => {
    if (connected && conversationsStore.activeConversationId !== null) {
      chatSocket.subscribeDialog(conversationsStore.activeConversationId);
    }
  },
);
</script>

<template>
  <AppLayout>
    <LoadingState v-if="conversationsStore.isLoading" />
    <div v-else class="workspace">
      <aside class="workspace__sidebar">
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
          :is-connected="chatSocket.isConnected.value"
          :socket-error="chatSocket.lastError.value"
          @send-message="handleSendMessage"
          @load-older="handleLoadOlder"
        />
      </section>
    </div>
  </AppLayout>
</template>

<style scoped>
.workspace {
  display: grid;
  grid-template-columns: 320px 1fr;
  height: calc(100vh - 73px);
  margin: -1rem;
}

.workspace__sidebar,
.workspace__main {
  min-height: 0;
}
</style>
