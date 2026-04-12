from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi import WebSocket, WebSocketDisconnect

from app.models import (
    ConductorEnabledRequest,
    ConductorEnabledStatus,
    ConductorStartRequest,
    ConductorStatus,
    ConductorStopRequest,
    ConductorTempoRequest,
    ServiceToggleRequest,
    ServiceToggleStatus,
    TempoCommand,
)
from app.service import ConductorRuntime
from app.system_logs import recent_logs

router = APIRouter()
runtime: ConductorRuntime | None = None


def set_runtime(value: ConductorRuntime) -> None:
    global runtime
    runtime = value


def _runtime() -> ConductorRuntime:
    if runtime is None:
        raise HTTPException(status_code=503, detail="Conductor runtime unavailable")
    return runtime




@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "conductor"}


@router.post("/v1/conductor/start", response_model=ConductorStatus)
def start(payload: ConductorStartRequest) -> ConductorStatus:
    try:
        return _runtime().start(payload)
    except RuntimeError as exc:
        if str(exc) == "conductor_disabled":
            raise HTTPException(status_code=409, detail="Conductor is disabled") from exc
        raise


@router.post("/v1/conductor/stop", response_model=ConductorStatus)
def stop(payload: ConductorStopRequest) -> ConductorStatus:
    return _runtime().stop(payload.session_id)


@router.post("/v1/conductor/tempo", response_model=ConductorStatus)
def tempo(payload: ConductorTempoRequest) -> ConductorStatus:
    command = TempoCommand(
        session_id=payload.session_id,
        new_bpm=payload.new_bpm,
        issued_by=payload.issued_by,
    )
    return _runtime().set_tempo(command)


@router.get("/v1/conductor/status", response_model=ConductorStatus)
def status() -> ConductorStatus:
    return _runtime().status()


@router.get("/v1/conductor/enabled", response_model=ConductorEnabledStatus)
def enabled_status() -> ConductorEnabledStatus:
    return ConductorEnabledStatus(enabled=_runtime().is_enabled())


@router.post("/v1/conductor/enabled", response_model=ConductorEnabledStatus)
def set_enabled(payload: ConductorEnabledRequest) -> ConductorEnabledStatus:
    enabled = _runtime().set_enabled(payload.enabled)
    return ConductorEnabledStatus(enabled=enabled)


@router.get("/v1/conductor/services")
def services_status() -> dict:
    return {"items": _runtime().service_control_status()}


@router.post("/v1/conductor/services/control", response_model=ServiceToggleStatus)
def services_control(payload: ServiceToggleRequest) -> ServiceToggleStatus:
    try:
        result = _runtime().set_service_enabled(payload.service_name, payload.enabled)
        return ServiceToggleStatus(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Failed to toggle service: {exc}") from exc


@router.get("/v1/conductor/logs")
def system_logs(limit: int = 200) -> dict:
    return {"items": recent_logs(limit)}


@router.get("/v1/conductor/audio/latest")
def latest_audio() -> Response:
    try:
        content, media_type = _runtime().fetch_latest_audio()
        return Response(content=content, media_type=media_type)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Failed to fetch audio: {exc}") from exc


@router.websocket("/v1/conductor/audio/stream")
async def audio_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    runtime = _runtime()
    settings = runtime.settings
    connection = None
    channel = None
    try:
        import asyncio
        import json
        import pika

        params = pika.URLParameters(settings.rabbitmq_url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(exchange=settings.exchange_name, exchange_type="topic", durable=True)
        queue = channel.queue_declare(queue="", exclusive=True, auto_delete=True).method.queue
        channel.queue_bind(exchange=settings.exchange_name, queue=queue, routing_key="playback.output")
        channel.basic_qos(prefetch_count=300)

        while True:
            method, properties, body = channel.basic_get(queue=queue, auto_ack=False)
            if method is None:
                await asyncio.sleep(0.01)
                continue

            try:
                payload = json.loads(body)
                event = payload if isinstance(payload, dict) else {}
                instrument = str(event.get("instrument", "guitar"))
                if not runtime.is_instrument_enabled(instrument):
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                    continue

                await websocket.send_json(
                    {
                        "instrument": instrument,
                        "pitch": int(event.get("pitch", 69)),
                        "duration": float(event.get("duration", 0.18)),
                        "volume": int(event.get("volume", 90)),
                    }
                )
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except WebSocketDisconnect:
        return
    finally:
        try:
            if channel is not None and channel.is_open:
                channel.close()
        except Exception:
            pass
        try:
            if connection is not None and connection.is_open:
                connection.close()
        except Exception:
            pass


@router.get("/ui", response_class=HTMLResponse)
def ui_index() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Conductor Control</title>
    <style>
      body { font-family: Helvetica, sans-serif; margin: 20px; background: #f4f6f8; color: #1a1f2b; }
      .card { background: #fff; border: 1px solid #d9e0e8; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
      button { margin-right: 8px; padding: 6px 10px; border-radius: 8px; border: 1px solid #bcc7d6; background: #fdfefe; cursor: pointer; }
      pre { background: #10151f; color: #d5e2ff; padding: 10px; border-radius: 8px; max-height: 320px; overflow: auto; }
      .row { display: flex; gap: 10px; flex-wrap: wrap; }
    </style>
  </head>
  <body>
    <h2>Conductor Control Panel</h2>
    <div class='card'>
      <h3>Instrument Services</h3>
      <div class='row'>
        <button onclick="toggleService('guitar-service', true)">Start guitar-service</button>
        <button onclick="toggleService('guitar-service', false)">Stop guitar-service</button>
        <button onclick="toggleService('oboe-service', true)">Start oboe-service</button>
        <button onclick="toggleService('oboe-service', false)">Stop oboe-service</button>
        <button onclick="toggleService('drums-service', true)">Start drums-service</button>
        <button onclick="toggleService('drums-service', false)">Stop drums-service</button>
        <button onclick="toggleService('mixer', true)">Start mixer</button>
        <button onclick="toggleService('mixer', false)">Stop mixer</button>
      </div>
      <pre id='services'></pre>
    </div>
    <div class='card'>
      <h3>System Logs</h3>
      <pre id='logs'></pre>
    </div>
    <div class='card'>
      <h3>Live Audio Stream</h3>
      <div class='row'>
        <button onclick='startStream()'>Start stream</button>
        <button onclick='stopStream()'>Stop stream</button>
      </div>
      <pre id='audio-status'></pre>
    </div>
    <script>
      async function refresh() {
        const svc = await fetch('/v1/conductor/services').then(r => r.json());
        document.getElementById('services').textContent = JSON.stringify(svc, null, 2);
        const logs = await fetch('/v1/conductor/logs?limit=120').then(r => r.json());
        document.getElementById('logs').textContent = JSON.stringify(logs, null, 2);
      }
      async function toggleService(name, enabled) {
        await fetch('/v1/conductor/services/control', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({service_name: name, enabled})
        });
        await refresh();
      }
      let ws = null;
      let audioCtx = null;
      let masterGain = null;

      function midiToFreq(pitch) {
        return 440 * Math.pow(2, (pitch - 69) / 12);
      }

      function instrumentWave(instrument) {
        if (instrument === 'oboe') return 'triangle';
        if (instrument === 'bass') return 'sawtooth';
        return 'sine';
      }

      function playDrum(duration, volume) {
        const bufferSize = Math.max(256, Math.floor(audioCtx.sampleRate * Math.min(0.25, duration)));
        const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
        const data = buffer.getChannelData(0);
        const amp = Math.min(1, Math.max(0.08, volume / 127));
        for (let i = 0; i < bufferSize; i++) {
          const env = 1 - i / bufferSize;
          data[i] = (Math.random() * 2 - 1) * env * amp;
        }
        const src = audioCtx.createBufferSource();
        const gain = audioCtx.createGain();
        gain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(amp, audioCtx.currentTime + 0.005);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + Math.min(0.2, duration + 0.03));
        src.buffer = buffer;
        src.connect(gain).connect(masterGain);
        src.start();
        src.stop(audioCtx.currentTime + Math.min(0.25, duration + 0.04));
      }

      function playTone(ev) {
        const instrument = ev.instrument || 'guitar';
        const pitch = Number(ev.pitch || 69);
        const duration = Math.max(0.03, Math.min(0.7, Number(ev.duration || 0.2)));
        const volume = Math.max(1, Math.min(127, Number(ev.volume || 90)));
        if (instrument === 'drums') {
          playDrum(duration, volume);
          return;
        }

        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = instrumentWave(instrument);
        osc.frequency.setValueAtTime(midiToFreq(pitch), audioCtx.currentTime);

        const amp = Math.min(0.9, Math.max(0.05, volume / 127));
        const attack = 0.008;
        const release = Math.min(0.3, duration * 0.75 + 0.04);
        gain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(amp, audioCtx.currentTime + attack);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration + release);

        osc.connect(gain).connect(masterGain);
        osc.start();
        osc.stop(audioCtx.currentTime + duration + release + 0.02);
      }

      async function startStream() {
        const status = document.getElementById('audio-status');
        if (!audioCtx) {
          audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 22050 });
          masterGain = audioCtx.createGain();
          masterGain.gain.value = 0.9;
          masterGain.connect(audioCtx.destination);
        }
        if (audioCtx.state !== 'running') {
          await audioCtx.resume();
        }
        if (ws && ws.readyState === WebSocket.OPEN) {
          status.textContent = 'Stream already running';
          return;
        }
        const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
        ws = new WebSocket(`${protocol}://${location.host}/v1/conductor/audio/stream`);
        ws.onopen = () => { status.textContent = 'Live stream connected'; };
        ws.onmessage = (event) => {
          try {
            const ev = JSON.parse(event.data);
            playTone(ev);
          } catch (e) {
          }
        };
        ws.onclose = () => { status.textContent = 'Stream stopped'; };
        ws.onerror = () => { status.textContent = 'Stream error'; };
      }

      function stopStream() {
        const status = document.getElementById('audio-status');
        if (ws) {
          ws.close();
          ws = null;
        }
        status.textContent = 'Stream stopped by user';
      }
      refresh();
      setTimeout(startStream, 800);
      setInterval(refresh, 3000);
    </script>
  </body>
</html>
"""
