import type { Fan, ModelAccountShort, UserShort } from "@/types/conversations";
import type { Message } from "@/types/messages";

export interface LeadConversation {
  id: number;
  fan: Fan;
  model_account: ModelAccountShort;
  assigned_chatter: UserShort;
  status: string;
  last_message: Message | null;
  last_message_at: string | null;
  unread_count_for_assigned_chatter: number;
  waiting_since: string | null;
  last_fan_message_at: string | null;
  last_chatter_message_at: string | null;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface LeadConversationListResponse {
  count: number;
  results: LeadConversation[];
}

export interface LeadConversationFilters {
  search?: string;
  status?: "ACTIVE" | "CLOSED" | "";
  assigned_chatter_id?: number | "";
  model_account_id?: number | "";
  limit?: number;
  offset?: number;
}

export interface LeadChatterWorkload {
  id: number;
  username: string;
  display_name: string;
  is_online: boolean;
  active_conversations_count: number;
  waiting_conversations_count: number;
  overdue_conversations_count: number;
  last_seen_at: string | null;
}

export interface LeadChatterWorkloadResponse {
  results: LeadChatterWorkload[];
}
