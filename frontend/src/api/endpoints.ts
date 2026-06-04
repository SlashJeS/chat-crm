export const AUTH_TOKEN = "/auth/token/";
export const AUTH_REFRESH = "/auth/token/refresh/";
export const ME = "/me/";
export const CONVERSATIONS = "/conversations/";
export const DEV_SIMULATE_FAN_MESSAGE = "/dev/simulate-fan-message/";
export const MONITOR_SNAPSHOT = "/monitor/snapshot/";
export const LEAD_CONVERSATIONS = "/lead/conversations/";
export const LEAD_CHATTERS_WORKLOAD = "/lead/chatters/workload/";

export const conversationDetail = (id: number) => `/conversations/${id}/`;
export const conversationMessages = (id: number) => `/conversations/${id}/messages/`;
export const conversationRead = (id: number) => `/conversations/${id}/read/`;
export const leadConversationDetail = (id: number) => `/lead/conversations/${id}/`;
export const leadConversationAssign = (id: number) => `/lead/conversations/${id}/assign/`;

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
  monitorSnapshot: MONITOR_SNAPSHOT,
  monitor: "/monitor/",
  leadConversations: LEAD_CONVERSATIONS,
  leadConversationDetail,
  leadConversationAssign,
  leadChattersWorkload: LEAD_CHATTERS_WORKLOAD,
} as const;
