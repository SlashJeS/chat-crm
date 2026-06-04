import type { Message } from "@/types/messages";

export interface Fan {
  id: number;
  external_id: string;
  display_name: string;
  avatar_url: string;
}

export interface ModelAccountShort {
  id: number;
  name: string;
  avatar_url: string;
}

export interface UserShort {
  id: number;
  username: string;
  display_name: string;
}

export interface Conversation {
  id: number;
  fan: Fan;
  model_account: ModelAccountShort;
  assigned_chatter: UserShort;
  status: string;
  last_message: Message | null;
  last_message_at: string | null;
  unread_count: number;
  waiting_since: string | null;
  last_fan_message_at: string | null;
  last_chatter_message_at: string | null;
  is_overdue: boolean;
}

export interface ConversationReadState {
  last_read_message: Message | null;
  last_read_at: string | null;
  unread_count: number;
}

export interface MessagesPageResponse {
  results: Message[];
  has_more: boolean;
  next_before_id: number | null;
}
