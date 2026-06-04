export type InviteRole = "CHATTER" | "TEAMLEAD";

export type InviteStatus = "active" | "accepted" | "revoked" | "expired";

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  last_login: string | null;
  role: "CHATTER" | "TEAMLEAD" | "ADMIN";
  display_name: string;
  last_seen_at: string | null;
  profile_created_at: string;
}

export interface AdminUserListResponse {
  count: number;
  results: AdminUser[];
}

export interface InviteUserSummary {
  id: number;
  username: string;
  email: string;
}

export interface UserInvite {
  id: number;
  token: string;
  email: string;
  role: InviteRole;
  invited_by: InviteUserSummary | null;
  accepted_by: InviteUserSummary | null;
  is_revoked: boolean;
  expires_at: string;
  accepted_at: string | null;
  created_at: string;
  is_expired: boolean;
  is_accepted: boolean;
  is_active_invite: boolean;
  invite_url: string;
  status?: InviteStatus;
}

export interface UserInviteListResponse {
  count: number;
  results: UserInvite[];
}

export interface CreateInvitePayload {
  email?: string;
  role: InviteRole;
  expires_in_hours: number;
}

export interface PublicInvite {
  token: string;
  email: string;
  role: InviteRole;
  expires_at: string;
  is_active_invite: boolean;
  status: InviteStatus;
}

export interface AcceptInvitePayload {
  username: string;
  display_name?: string;
  email?: string;
  password: string;
  password_confirm: string;
}

export interface AcceptInviteResponse {
  message: string;
}
