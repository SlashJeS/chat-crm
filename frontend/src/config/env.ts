function requiredEnv(name: keyof ImportMetaEnv): string {
  const value = import.meta.env[name];
  if (value === undefined || value === null || String(value).trim() === "") {
    throw new Error(`Missing required environment variable: ${String(name)}`);
  }
  return String(value).trim();
}

export const API_BASE_URL = requiredEnv("VITE_API_BASE_URL");

const wsConfiguredValue = requiredEnv("VITE_WS_BASE_URL");

export function resolveWebSocketBaseUrl(): string {
  if (wsConfiguredValue === "auto") {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}`;
  }
  return wsConfiguredValue;
}
