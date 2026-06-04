export interface MonitorChatter {
  id: number;
  username: string;
  display_name: string;
  role: "CHATTER";
  is_online: boolean;
  active_conversations_count: number;
  waiting_conversations_count: number;
  overdue_conversations_count: number;
  last_seen_at: string | null;
}

export interface MonitorSnapshot {
  sla_seconds: number;
  presence_grace_seconds: number;
  chatters: MonitorChatter[];
}
