import { ref } from "vue";

import { createSocketClient } from "@/websocket/socket";

export function useChatSocket() {
  const isConnected = ref(false);
  const socket = createSocketClient("ws://localhost:8000/ws/chat/");

  return {
    isConnected,
    socket,
  };
}
