import type { UserShort } from "@/types/conversations";

export type MessageSenderType = "FAN" | "CHATTER" | "SYSTEM";
export type MessageType = "TEXT" | "PPV";
export type MessageLocalStatus = "pending" | "sent" | "failed";

export interface Message {
  id: number;
  conversation: number;
  sender_type: MessageSenderType;
  sender_user: UserShort | null;
  message_type: MessageType;
  text: string;
  ppv_price: string | null;
  client_message_id: string | null;
  created_at: string;
  local_status?: MessageLocalStatus;
}

export interface SendMessagePayload {
  type: "message.send";
  conversation_id: number;
  message_type: MessageType;
  text: string;
  ppv_price?: string | null;
  client_message_id: string;
}
