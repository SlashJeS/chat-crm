export type ConnectionState =
  | "idle"
  | "connecting"
  | "connected"
  | "disconnected"
  | "reconnecting"
  | "closed";

export interface SocketClientOptions {
  autoReconnect?: boolean;
  maxReconnectAttempts?: number | null;
  initialReconnectDelayMs?: number;
  maxReconnectDelayMs?: number;
}

type MessageHandler = (data: Record<string, unknown>) => void;
type VoidHandler = () => void;
type StateHandler = (state: ConnectionState) => void;
type ReconnectAttemptHandler = (attempt: number) => void;

const DEFAULT_OPTIONS: Required<SocketClientOptions> = {
  autoReconnect: true,
  maxReconnectAttempts: null,
  initialReconnectDelayMs: 500,
  maxReconnectDelayMs: 5000,
};

export class SocketClient {
  private socket: WebSocket | null = null;
  private url = "";
  private options: Required<SocketClientOptions> = { ...DEFAULT_OPTIONS };
  private manualClose = false;
  private hasConnectedBefore = false;
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private state: ConnectionState = "idle";

  private messageHandlers: MessageHandler[] = [];
  private openHandlers: VoidHandler[] = [];
  private closeHandlers: VoidHandler[] = [];
  private errorHandlers: Array<(event: Event) => void> = [];
  private stateHandlers: StateHandler[] = [];
  private reconnectAttemptHandlers: ReconnectAttemptHandler[] = [];
  private reconnectSuccessHandlers: VoidHandler[] = [];
  private reconnectFailedHandlers: VoidHandler[] = [];

  get connected(): boolean {
    return this.state === "connected";
  }

  get connectionState(): ConnectionState {
    return this.state;
  }

  get currentReconnectAttempt(): number {
    return this.reconnectAttempts;
  }

  configure(options: SocketClientOptions): void {
    this.options = { ...DEFAULT_OPTIONS, ...options };
  }

  connect(url: string): void {
    this.url = url;
    this.manualClose = false;
    this.clearReconnectTimer();
    this.openSocket(false);
  }

  disconnect(): void {
    this.manualClose = true;
    this.clearReconnectTimer();
    this.closeSocket();
    this.setState("closed");
  }

  send(data: unknown): boolean {
    if (!this.connected || !this.socket) {
      return false;
    }
    this.socket.send(JSON.stringify(data));
    return true;
  }

  onMessage(handler: MessageHandler): void {
    this.messageHandlers.push(handler);
  }

  onOpen(handler: VoidHandler): void {
    this.openHandlers.push(handler);
  }

  onClose(handler: VoidHandler): void {
    this.closeHandlers.push(handler);
  }

  onError(handler: (event: Event) => void): void {
    this.errorHandlers.push(handler);
  }

  onStateChange(handler: StateHandler): void {
    this.stateHandlers.push(handler);
  }

  onReconnectAttempt(handler: ReconnectAttemptHandler): void {
    this.reconnectAttemptHandlers.push(handler);
  }

  onReconnectSuccess(handler: VoidHandler): void {
    this.reconnectSuccessHandlers.push(handler);
  }

  onReconnectFailed(handler: VoidHandler): void {
    this.reconnectFailedHandlers.push(handler);
  }

  private openSocket(isReconnect: boolean): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.closeSocket();
    this.setState(isReconnect ? "reconnecting" : "connecting");
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      const wasReconnect = isReconnect || this.reconnectAttempts > 0;
      this.reconnectAttempts = 0;
      this.setState("connected");
      this.openHandlers.forEach((handler) => handler());
      if (wasReconnect && this.hasConnectedBefore) {
        this.reconnectSuccessHandlers.forEach((handler) => handler());
      }
      this.hasConnectedBefore = true;
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(String(event.data)) as Record<string, unknown>;
        this.messageHandlers.forEach((handler) => handler(data));
      } catch {
        this.messageHandlers.forEach((handler) => handler({ type: "raw", data: event.data }));
      }
    };

    this.socket.onclose = () => {
      this.socket = null;
      this.closeHandlers.forEach((handler) => handler());

      if (this.manualClose) {
        this.setState("closed");
        return;
      }

      this.setState("disconnected");
      this.scheduleReconnect();
    };

    this.socket.onerror = (event) => {
      this.errorHandlers.forEach((handler) => handler(event));
    };
  }

  private scheduleReconnect(): void {
    if (!this.options.autoReconnect || this.manualClose || !this.url) {
      return;
    }

    this.reconnectAttempts += 1;

    if (
      this.options.maxReconnectAttempts !== null &&
      this.reconnectAttempts > this.options.maxReconnectAttempts
    ) {
      this.setState("disconnected");
      this.reconnectFailedHandlers.forEach((handler) => handler());
      return;
    }

    this.reconnectAttemptHandlers.forEach((handler) => handler(this.reconnectAttempts));

    const delay = Math.min(
      this.options.initialReconnectDelayMs * 2 ** (this.reconnectAttempts - 1),
      this.options.maxReconnectDelayMs,
    );
    const jitter = Math.floor(Math.random() * 100);

    this.clearReconnectTimer();
    this.reconnectTimer = setTimeout(() => {
      if (!this.manualClose) {
        this.openSocket(true);
      }
    }, delay + jitter);
  }

  private closeSocket(): void {
    if (!this.socket) {
      return;
    }
    this.socket.onopen = null;
    this.socket.onmessage = null;
    this.socket.onclose = null;
    this.socket.onerror = null;
    this.socket.close();
    this.socket = null;
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private setState(nextState: ConnectionState): void {
    this.state = nextState;
    this.stateHandlers.forEach((handler) => handler(nextState));
  }
}

export function createSocketClient(options?: SocketClientOptions): SocketClient {
  const client = new SocketClient();
  if (options) {
    client.configure(options);
  }
  return client;
}

export function connectionStateLabel(state: ConnectionState): string {
  switch (state) {
    case "connected":
      return "Connected";
    case "connecting":
      return "Connecting";
    case "reconnecting":
      return "Reconnecting";
    case "disconnected":
      return "Disconnected";
    case "closed":
      return "Disconnected";
    default:
      return "Idle";
  }
}
