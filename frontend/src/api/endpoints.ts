export const AUTH_TOKEN = "/auth/token/";
export const AUTH_REFRESH = "/auth/token/refresh/";
export const ME = "/me/";

export const endpoints = {
  health: "/health/",
  me: ME,
  auth: {
    token: AUTH_TOKEN,
    refresh: AUTH_REFRESH,
  },
  conversations: "/conversations/",
  messages: (conversationId: number) => `/conversations/${conversationId}/messages/`,
  monitor: "/monitor/",
} as const;
