type MessageHandler = (data: Record<string, unknown>) => void;
type VoidHandler = () => void;

export class SocketClient {
  private socket: WebSocket | null = null;
  private messageHandlers: MessageHandler[] = [];
  private openHandlers: VoidHandler[] = [];
  private closeHandlers: VoidHandler[] = [];
  private errorHandlers: Array<(event: Event) => void> = [];

  get connected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  connect(url: string): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.disconnect();
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      this.openHandlers.forEach((handler) => handler());
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
      this.closeHandlers.forEach((handler) => handler());
    };

    this.socket.onerror = (event) => {
      this.errorHandlers.forEach((handler) => handler(event));
    };
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.onopen = null;
      this.socket.onmessage = null;
      this.socket.onclose = null;
      this.socket.onerror = null;
      this.socket.close();
      this.socket = null;
    }
  }

  send(data: unknown): boolean {
    if (!this.connected) {
      return false;
    }
    this.socket?.send(JSON.stringify(data));
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

  clearHandlers(): void {
    this.messageHandlers = [];
    this.openHandlers = [];
    this.closeHandlers = [];
    this.errorHandlers = [];
  }
}

export function createSocketClient(): SocketClient {
  return new SocketClient();
}
