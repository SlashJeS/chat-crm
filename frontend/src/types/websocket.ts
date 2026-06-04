import type { Conversation, ConversationReadState } from "@/types/conversations";
import type { Message } from "@/types/messages";

export interface WsConnectionAcceptedEvent {
  type: "connection.accepted";
}

export interface WsDialogSubscribedEvent {
  type: "dialog.subscribed";
  conversation_id: number;
}

export interface WsDialogUnsubscribedEvent {
  type: "dialog.unsubscribed";
  conversation_id: number;
}

export interface WsMessageSendAckEvent {
  type: "message.send.ack";
  client_message_id: string | null;
  message_id: number;
}

export interface WsDialogMarkReadAckEvent {
  type: "dialog.mark_read.ack";
  conversation_id: number;
}

export interface WsMessageCreatedEvent {
  type: "message.created";
  message: Message;
}

export interface WsConversationUpdatedEvent {
  type: "conversation.updated";
  conversation: Conversation;
}

export interface WsReadStateUpdatedEvent {
  type: "conversation.read_state.updated";
  conversation_id: number;
  read_state: ConversationReadState;
}

export interface WsErrorEvent {
  type: "error";
  code: string;
  message: string;
}

export type WsServerEvent =
  | WsConnectionAcceptedEvent
  | WsDialogSubscribedEvent
  | WsDialogUnsubscribedEvent
  | WsMessageSendAckEvent
  | WsDialogMarkReadAckEvent
  | WsMessageCreatedEvent
  | WsConversationUpdatedEvent
  | WsReadStateUpdatedEvent
  | WsErrorEvent;

export interface WebSocketEvent<T = unknown> {
  type: string;
  payload?: T;
}
