import { computed, ref } from "vue";

import { ACCESS_TOKEN_KEY } from "@/api/http";
import { WS_BASE_URL } from "@/config/env";
import { useAuthStore } from "@/stores/auth.store";
import { useMonitorStore } from "@/stores/monitor.store";
import type { MonitorSnapshot } from "@/types/monitor";
import type { WsMonitorSnapshotEvent, WsErrorEvent } from "@/types/websocket";
import {
  connectionStateLabel,
  createSocketClient,
  type ConnectionState,
  type SocketClient,
} from "@/websocket/socket";

let socketClient: SocketClient | null = null;

const connectionState = ref<ConnectionState>("idle");
const reconnectAttempt = ref(0);
const lastError = ref<string | null>(null);

function getSocketUrl(): string {
  const auth = useAuthStore();
  const token = auth.accessToken ?? localStorage.getItem(ACCESS_TOKEN_KEY);
  return `${WS_BASE_URL}/ws/monitor/?token=${token}`;
}

function handleServerEvent(data: Record<string, unknown>): void {
  const monitorStore = useMonitorStore();
  const eventType = data.type as string | undefined;

  if (eventType === "monitor.snapshot") {
    const event = data as unknown as WsMonitorSnapshotEvent;
    monitorStore.applySnapshot(event.snapshot);
    return;
  }

  if (eventType === "error") {
    const event = data as unknown as WsErrorEvent;
    lastError.value = event.message;
  }
}

async function resyncAfterReconnect(): Promise<void> {
  const monitorStore = useMonitorStore();
  lastError.value = null;
  await monitorStore.loadSnapshot();
  socketClient?.send({ type: "monitor.refresh" });
}

export function useMonitorSocket() {
  const auth = useAuthStore();

  function ensureClient(): SocketClient {
    if (!socketClient) {
      socketClient = createSocketClient({ autoReconnect: true });

      socketClient.onStateChange((state) => {
        connectionState.value = state;
      });

      socketClient.onOpen(() => {
        lastError.value = null;
      });

      socketClient.onReconnectAttempt((attempt) => {
        reconnectAttempt.value = attempt;
        lastError.value = `Reconnecting (${attempt})...`;
      });

      socketClient.onReconnectSuccess(async () => {
        reconnectAttempt.value = 0;
        try {
          await resyncAfterReconnect();
        } catch {
          lastError.value = "Failed to resync monitor after reconnect";
        }
      });

      socketClient.onReconnectFailed(() => {
        lastError.value = "Unable to reconnect to monitor server";
      });

      socketClient.onError(() => {
        if (connectionState.value !== "reconnecting") {
          lastError.value = "WebSocket connection error";
        }
      });

      socketClient.onMessage(handleServerEvent);
    }
    return socketClient;
  }

  function connect(): void {
    if (!auth.accessToken) {
      lastError.value = "Not authenticated";
      return;
    }
    ensureClient().connect(getSocketUrl());
  }

  function disconnect(): void {
    socketClient?.disconnect();
    connectionState.value = "closed";
    reconnectAttempt.value = 0;
  }

  function refresh(): void {
    const sent = ensureClient().send({ type: "monitor.refresh" });
    if (!sent) {
      lastError.value = "WebSocket is not connected";
    }
  }

  return {
    connect,
    disconnect,
    refresh,
    isConnected: computed(() => connectionState.value === "connected"),
    connectionState: computed(() => connectionState.value),
    connectionLabel: computed(() => connectionStateLabel(connectionState.value)),
    reconnectAttempt: computed(() => reconnectAttempt.value),
    lastError: computed(() => lastError.value),
  };
}

export type { MonitorSnapshot };
