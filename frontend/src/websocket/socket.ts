import type { WebSocketEvent } from "@/types/websocket";

type MessageHandler = (event: WebSocketEvent) => void;
type VoidHandler = () => void;

export class SocketClient {
  private socket: WebSocket | null = null;
  private messageHandlers: MessageHandler[] = [];
  private openHandlers: VoidHandler[] = [];
  private closeHandlers: VoidHandler[] = [];
  private errorHandlers: Array<(event: Event) => void> = [];

  constructor(private readonly url: string) {}

  connect(): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      this.openHandlers.forEach((handler) => handler());
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(String(event.data)) as WebSocketEvent;
        this.messageHandlers.forEach((handler) => handler(data));
      } catch {
        this.messageHandlers.forEach((handler) =>
          handler({ type: "raw", payload: event.data }),
        );
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
    this.socket?.close();
    this.socket = null;
  }

  send(data: unknown): void {
    if (this.socket?.readyState !== WebSocket.OPEN) {
      return;
    }
    this.socket.send(JSON.stringify(data));
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
}

export function createSocketClient(url: string): SocketClient {
  return new SocketClient(url);
}
