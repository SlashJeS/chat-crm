export interface Message {
  id: number;
  conversationId: number;
  body: string;
  senderType: "fan" | "chatter" | "system";
  createdAt: string;
}
