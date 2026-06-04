export const endpoints = {
  health: "/health/",
  me: "/me/",
  auth: {
    token: "/auth/token/",
    refresh: "/auth/token/refresh/",
  },
  conversations: "/conversations/",
  messages: (conversationId: number) => `/conversations/${conversationId}/messages/`,
  monitor: "/monitor/",
} as const;
