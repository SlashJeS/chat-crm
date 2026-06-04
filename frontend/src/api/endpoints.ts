export const AUTH_TOKEN = "/auth/token/";
export const AUTH_REFRESH = "/auth/token/refresh/";
export const ME = "/me/";
export const CONVERSATIONS = "/conversations/";
export const MONITOR_SNAPSHOT = "/monitor/snapshot/";
export const LEAD_CONVERSATIONS = "/lead/conversations/";
export const LEAD_CHATTERS_WORKLOAD = "/lead/chatters/workload/";

export const ADMIN_USERS = "/admin/users/";
export const ADMIN_INVITES = "/admin/invites/";

export const conversationDetail = (id: number) => `/conversations/${id}/`;
export const conversationMessages = (id: number) => `/conversations/${id}/messages/`;
export const conversationRead = (id: number) => `/conversations/${id}/read/`;
export const leadConversationDetail = (id: number) => `/lead/conversations/${id}/`;
export const leadConversationAssign = (id: number) => `/lead/conversations/${id}/assign/`;

export const adminUserDetail = (id: number) => `/admin/users/${id}/`;
export const adminUserUpdate = (id: number) => `/admin/users/${id}/update/`;
export const adminUserDeactivate = (id: number) => `/admin/users/${id}/deactivate/`;
export const adminUserActivate = (id: number) => `/admin/users/${id}/activate/`;
export const adminInviteRevoke = (id: number) => `/admin/invites/${id}/revoke/`;
export const publicInviteDetail = (token: string) => `/invites/${token}/`;
export const publicInviteAccept = (token: string) => `/invites/${token}/accept/`;

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
  monitorSnapshot: MONITOR_SNAPSHOT,
  monitor: "/monitor/",
  leadConversations: LEAD_CONVERSATIONS,
  leadConversationDetail,
  leadConversationAssign,
  leadChattersWorkload: LEAD_CHATTERS_WORKLOAD,
  adminUsers: ADMIN_USERS,
  adminInvites: ADMIN_INVITES,
  adminUserDetail,
  adminUserUpdate,
  adminUserDeactivate,
  adminUserActivate,
  adminInviteRevoke,
  publicInviteDetail,
  publicInviteAccept,
} as const;
