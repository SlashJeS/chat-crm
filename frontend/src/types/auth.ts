export type UserRole = "CHATTER" | "TEAMLEAD" | "ADMIN";

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  display_name: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}
