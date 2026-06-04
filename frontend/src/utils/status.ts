import type { MonitorChatter } from "@/types/monitor";
import { connectionStateLabel, type ConnectionState } from "@/websocket/socket";

export type StatusTone = "success" | "warning" | "danger" | "muted";

export type MonitorChatterStatus = "Healthy" | "Waiting" | "Overdue" | "Offline";

export function getMonitorChatterStatus(chatter: MonitorChatter): MonitorChatterStatus {
  if (!chatter.is_online) {
    return "Offline";
  }
  if (chatter.overdue_conversations_count > 0) {
    return "Overdue";
  }
  if (chatter.waiting_conversations_count > 0) {
    return "Waiting";
  }
  return "Healthy";
}

export function getConnectionLabel(state: ConnectionState): string {
  return connectionStateLabel(state);
}

export function getRealtimeConnectionLabel(state: ConnectionState): string {
  switch (state) {
    case "connected":
      return "Realtime connected";
    case "connecting":
      return "Connecting to realtime";
    case "reconnecting":
      return "Realtime reconnecting";
    case "disconnected":
    case "closed":
      return "Realtime disconnected";
    default:
      return "Realtime idle";
  }
}

export function getConnectionTone(state: ConnectionState, hasError = false): StatusTone {
  if (state === "connected") {
    return "success";
  }
  if (state === "reconnecting" || state === "connecting") {
    return "warning";
  }
  if (hasError || state === "disconnected") {
    return "danger";
  }
  return "muted";
}

export function formatThresholdSeconds(seconds: number): string {
  if (seconds >= 60) {
    const minutes = Math.floor(seconds / 60);
    const remainder = seconds % 60;
    if (remainder === 0) {
      return `${minutes} min`;
    }
    return `${minutes}m ${remainder}s`;
  }
  return `${seconds}s`;
}

export function monitorStatusTone(status: MonitorChatterStatus): StatusTone {
  switch (status) {
    case "Healthy":
      return "success";
    case "Waiting":
      return "warning";
    case "Overdue":
      return "danger";
    case "Offline":
      return "muted";
  }
}
