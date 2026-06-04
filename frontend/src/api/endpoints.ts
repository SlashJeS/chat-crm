export const AUTH_TOKEN = "/auth/token/";
export const AUTH_REFRESH = "/auth/token/refresh/";
export const ME = "/me/";
export const CONVERSATIONS = "/conversations/";
export const DEV_SIMULATE_FAN_MESSAGE = "/dev/simulate-fan-message/";

export const conversationDetail = (id: number) => `/conversations/${id}/`;
export const conversationMessages = (id: number) => `/conversations/${id}/messages/`;
export const conversationRead = (id: number) => `/conversations/${id}/read/`;

export const endpoints = {
  health: "/health/",
  me: ME,
  auth: {
    token: AUTH_TOKEN,
    refresh: AUTH_REFRESH,
  },
  conversations: CONVERSATIONS,
  conversationDetail,
  conversationMessages,
  conversationRead,
  devSimulateFanMessage: DEV_SIMULATE_FAN_MESSAGE,
  monitor: "/monitor/",
} as const;
