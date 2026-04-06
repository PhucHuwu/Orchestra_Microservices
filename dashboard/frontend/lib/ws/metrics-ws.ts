import { metricsWsSchema, type MetricsWsPayload } from "@/lib/api/contracts";

const DEFAULT_WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/metrics";

type Listener = (payload: MetricsWsPayload) => void;
type Status = "connected" | "disconnected" | "reconnecting";
type StatusListener = (status: Status) => void;

export class MetricsWsClient {
  private ws: WebSocket | null = null;
  private listener: Listener;
  private onStatus: StatusListener;
  private reconnectTimer: number | null = null;
  private disposed = false;

  constructor(listener: Listener, onStatus: StatusListener) {
    this.listener = listener;
    this.onStatus = onStatus;
  }

  connect() {
    if (this.disposed) {
      return;
    }

    this.ws = new WebSocket(DEFAULT_WS_URL);
    this.onStatus("reconnecting");

    this.ws.onopen = () => {
      this.onStatus("connected");
    };

    this.ws.onmessage = (event) => {
      try {
        const raw = JSON.parse(String(event.data));
        if (!raw?.success || !raw?.data) {
          return;
        }
        const parsed = metricsWsSchema.safeParse(raw.data);
        if (parsed.success) {
          this.listener(parsed.data);
        }
      } catch {
        this.onStatus("disconnected");
      }
    };

    this.ws.onclose = () => {
      this.onStatus("disconnected");
      this.scheduleReconnect();
    };

    this.ws.onerror = () => {
      this.onStatus("disconnected");
      this.ws?.close();
    };
  }

  dispose() {
    this.disposed = true;
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.ws?.close();
  }

  private scheduleReconnect() {
    if (this.disposed || this.reconnectTimer) {
      return;
    }

    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 1500);
  }
}
