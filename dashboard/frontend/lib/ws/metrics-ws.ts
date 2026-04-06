import { metricsWsSchema, type MetricsWsPayload } from "@/lib/api/contracts";

function resolveWsUrl(): string {
  if (typeof window !== "undefined") {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const pageHost = window.location.hostname;

    if (process.env.NEXT_PUBLIC_WS_URL) {
      try {
        const configured = new URL(process.env.NEXT_PUBLIC_WS_URL);
        const localHosts = new Set(["localhost", "127.0.0.1"]);
        if (localHosts.has(configured.hostname) && !localHosts.has(pageHost)) {
          return `${protocol}//${pageHost}:8000/ws/metrics`;
        }
        return `${configured.protocol}//${configured.host}${configured.pathname}`;
      } catch {
        // Fall through to next strategy.
      }
    }

    if (process.env.NEXT_PUBLIC_API_BASE_URL) {
      try {
        const api = new URL(process.env.NEXT_PUBLIC_API_BASE_URL);
        const localHosts = new Set(["localhost", "127.0.0.1"]);
        const targetHost = localHosts.has(api.hostname) && !localHosts.has(pageHost) ? pageHost : api.hostname;
        const targetPort = api.port || (api.protocol === "https:" ? "443" : "80");
        return `${protocol}//${targetHost}:${targetPort}/ws/metrics`;
      } catch {
        // Fall through to next strategy.
      }
    }

    return `${protocol}//${pageHost}:8000/ws/metrics`;
  }

  if (process.env.NEXT_PUBLIC_WS_URL) {
    return process.env.NEXT_PUBLIC_WS_URL;
  }

  return "ws://localhost:8000/ws/metrics";
}

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

    this.ws = new WebSocket(resolveWsUrl());
    this.onStatus("reconnecting");

    this.ws.onopen = () => {
      this.onStatus("connected");
    };

    this.ws.onmessage = (event) => {
      void this.handleMessage(event.data);
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
    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onclose = null;
      this.ws.onerror = null;
      if (this.ws.readyState === WebSocket.OPEN) {
        this.ws.close();
      }
      this.ws = null;
    }
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

  private async handleMessage(data: unknown): Promise<void> {
    try {
      let textPayload: string;
      if (typeof data === "string") {
        textPayload = data;
      } else if (data instanceof Blob) {
        textPayload = await data.text();
      } else {
        textPayload = String(data);
      }

      const raw = JSON.parse(textPayload);
      const candidate = raw?.data?.metrics ? raw.data : raw;
      const parsed = metricsWsSchema.safeParse(candidate);
      if (parsed.success) {
        this.listener(parsed.data);
      }
    } catch {
      // Ignore malformed WS frames; keep socket alive.
    }
  }
}
