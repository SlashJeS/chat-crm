<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from "vue";

import ChatWindow from "@/components/chat/ChatWindow.vue";
import DialogList from "@/components/chat/DialogList.vue";
import AppLayout from "@/components/common/AppLayout.vue";
import { useChatSocket } from "@/composables/useChatSocket";
import { useConversationsStore } from "@/stores/conversations.store";
import { useMessagesStore } from "@/stores/messages.store";
import type { SendMessagePayload } from "@/types/messages";

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
  await conversationsStore.loadConversations();
  chatSocket.connect();
});

watch(
  () => chatSocket.isConnected.value,
  (connected) => {
    const conversationId = conversationsStore.activeConversationId;
    if (connected && conversationId !== null) {
      chatSocket.subscribeDialog(conversationId);
    }
  },
);

onUnmounted(() => {
  if (previousConversationId !== null) {
    chatSocket.unsubscribeDialog(previousConversationId);
  }
  chatSocket.disconnect();
  conversationsStore.clear();
  messagesStore.clear();
});
</script>

<template>
  <AppLayout>
    <div class="workspace-page page">
      <div class="workspace">
        <aside class="workspace__sidebar panel">
          <DialogList
            :conversations="conversationsStore.conversations"
            :active-conversation-id="conversationsStore.activeConversationId"
            :loading="conversationsStore.isLoading"
            :error="conversationsStore.error"
            @select="handleSelectConversation"
            @retry="handleRetryConversations"
          />
        </aside>
        <section class="workspace__main panel">
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
            :socket-error="chatSocket.lastError.value"
            @send-message="handleSendMessage"
            @load-older="handleLoadOlder"
            @retry-messages="handleRetryMessages"
          />
        </section>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.workspace-page {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

@media (min-width: 901px) {
  .workspace-page {
    overflow: hidden;
  }
}

.workspace {
  display: grid;
  grid-template-columns: minmax(280px, 360px) minmax(0, 1fr);
  flex: 1 1 auto;
  min-height: 0;
  gap: var(--space-3);
}

@media (min-width: 901px) {
  .workspace {
    overflow: hidden;
  }
}

.workspace__sidebar,
.workspace__main {
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 0;
}

@media (min-width: 901px) {
  .workspace__sidebar,
  .workspace__main {
    overflow: hidden;
  }
}

@media (max-width: 900px) {
  .workspace {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
    gap: var(--space-3);
  }

  .workspace__sidebar {
    max-height: 40vh;
    overflow: hidden;
  }

  .workspace__main {
    min-height: 50vh;
    overflow: hidden;
  }
}

</style>
