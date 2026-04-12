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


def _decode_wav_to_pcm_mono(wav_data: bytes) -> tuple[int, bytes]:
    import io
    import wave

    if len(wav_data) <= 44:
        return 22050, b""

    with wave.open(io.BytesIO(wav_data), "rb") as wf:
        sample_rate = wf.getframerate()
        sample_width = wf.getsampwidth()
        channels = wf.getnchannels()
        raw = wf.readframes(wf.getnframes())

    if sample_width != 2:
        return sample_rate, b""
    if channels == 1:
        return sample_rate, raw

    out = bytearray(len(raw) // 2)
    dst = 0
    for i in range(0, len(raw), 4):
        l = int.from_bytes(raw[i : i + 2], "little", signed=True)
        r = int.from_bytes(raw[i + 2 : i + 4], "little", signed=True)
        m = (l + r) // 2
        out[dst : dst + 2] = int(m).to_bytes(2, "little", signed=True)
        dst += 2
    return sample_rate, bytes(out)


def _pcm_chunk(pcm: bytes, start_sample: int, chunk_samples: int) -> bytes:
    if len(pcm) == 0:
        return b"\x00" * (chunk_samples * 2)
    total = len(pcm) // 2
    if total <= 0:
        return b"\x00" * (chunk_samples * 2)

    start = start_sample % total
    need = chunk_samples
    out = bytearray(chunk_samples * 2)
    dst = 0
    pos = start
    while need > 0:
        take = min(need, total - pos)
        s = pos * 2
        e = s + (take * 2)
        out[dst : dst + (take * 2)] = pcm[s:e]
        dst += take * 2
        need -= take
        pos = 0
    return bytes(out)


def _mix_pcm_chunks(chunks: list[bytes], chunk_samples: int) -> bytes:
    if not chunks:
        return b"\x00" * (chunk_samples * 2)
    out = bytearray(chunk_samples * 2)
    for i in range(chunk_samples):
        mixed = 0
        byte_idx = i * 2
        for chunk in chunks:
            if byte_idx + 2 <= len(chunk):
                mixed += int.from_bytes(chunk[byte_idx : byte_idx + 2], "little", signed=True)
        if len(chunks) > 1:
            mixed = int(mixed / (len(chunks) ** 0.5))
        mixed = max(-32767, min(32767, mixed))
        out[byte_idx : byte_idx + 2] = int(mixed).to_bytes(2, "little", signed=True)
    return bytes(out)


def _crossfade_merge(old_pcm: bytes, new_pcm: bytes, fade_samples: int) -> bytes:
    if len(old_pcm) == 0:
        return new_pcm
    if len(new_pcm) == 0:
        return old_pcm

    old_total = len(old_pcm) // 2
    new_total = len(new_pcm) // 2
    if old_total <= 0 or new_total <= 0:
        return new_pcm

    fade = min(fade_samples, old_total, new_total)
    if fade <= 0:
        return new_pcm

    old_tail = old_pcm[(old_total - fade) * 2 :]
    suffix = new_pcm[fade * 2 :]
    blended = bytearray(fade * 2)
    for i in range(fade):
        old_idx = i * 2
        new_idx = i * 2
        a = int.from_bytes(old_tail[old_idx : old_idx + 2], "little", signed=True)
        b = int.from_bytes(new_pcm[new_idx : new_idx + 2], "little", signed=True)
        t = i / max(1, fade - 1)
        v = int((1.0 - t) * a + t * b)
        blended[i * 2 : i * 2 + 2] = int(v).to_bytes(2, "little", signed=True)

    return bytes(blended) + suffix

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
    try:
        import asyncio
        import hashlib
        import time

        runtime = _runtime()
        chunk_seconds = 0.04
        loop = asyncio.get_running_loop()
        next_tick = loop.time()
        stream_started = loop.time()
        sample_rate = 22050
        chunk_samples = int(sample_rate * chunk_seconds)
        stem_names = ["guitar", "oboe", "drums", "bass"]
        stem_pcm: dict[str, bytes] = {name: b"" for name in stem_names}
        stem_hash: dict[str, str] = {name: "" for name in stem_names}
        last_fetch = 0.0
        fetch_task: asyncio.Task | None = None
        while True:
            now = time.time()
            if now - last_fetch >= 0.15 and (fetch_task is None or fetch_task.done()):
                def _fetch_all_stems():
                    result: dict[str, bytes] = {}
                    for stem in stem_names:
                        try:
                            result[stem] = runtime.fetch_stem_audio(stem)[0]
                        except Exception:
                            result[stem] = b""
                    return result

                fetch_task = asyncio.create_task(asyncio.to_thread(_fetch_all_stems))
                last_fetch = now

            if fetch_task is not None and fetch_task.done():
                try:
                    result = fetch_task.result()
                    if isinstance(result, dict):
                        for stem in stem_names:
                            wav_data = result.get(stem, b"")
                            digest = hashlib.sha1(wav_data).hexdigest()
                            if digest != stem_hash[stem]:
                                sr, decoded = _decode_wav_to_pcm_mono(wav_data)
                                if len(decoded) > 0:
                                    sample_rate = sr
                                    chunk_samples = max(256, int(sample_rate * chunk_seconds))
                                    stem_pcm[stem] = decoded
                                    stem_hash[stem] = digest
                except Exception:
                    pass
                finally:
                    fetch_task = None

            enabled = runtime.stream_state().get("enabled", {})
            elapsed = max(0.0, loop.time() - stream_started)
            playhead_sample = int(elapsed * sample_rate)
            chunks: list[bytes] = []
            for stem in stem_names:
                if not bool(enabled.get(stem, True)):
                    continue
                chunk = _pcm_chunk(stem_pcm.get(stem, b""), playhead_sample, chunk_samples)
                chunks.append(chunk)

            payload = _mix_pcm_chunks(chunks, chunk_samples)
            await websocket.send_bytes(payload)
            next_tick += chunk_seconds
            await asyncio.sleep(max(0.0, next_tick - loop.time()))

    except WebSocketDisconnect:
        return
    except Exception:
        return


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
      let nextTime = 0;
      let pendingFrames = [];

      function schedulePendingFrames() {
        if (!audioCtx) return;
        if (pendingFrames.length > 14) {
          pendingFrames = pendingFrames.slice(-8);
          nextTime = audioCtx.currentTime + 0.12;
        }
        while (pendingFrames.length > 0 && (nextTime - audioCtx.currentTime) < 0.4) {
          const samples = pendingFrames.shift();
          const audioBuffer = audioCtx.createBuffer(1, samples.length, 22050);
          audioBuffer.getChannelData(0).set(samples);
          const src = audioCtx.createBufferSource();
          src.buffer = audioBuffer;
          src.connect(audioCtx.destination);
          if (nextTime < audioCtx.currentTime + 0.1) {
            nextTime = audioCtx.currentTime + 0.1;
          }
          src.start(nextTime);
          nextTime += audioBuffer.duration;
        }
      }

      function pcm16ToFloat32(buffer) {
        const input = new Int16Array(buffer);
        const out = new Float32Array(input.length);
        for (let i = 0; i < input.length; i++) {
          out[i] = input[i] / 32768;
        }
        return out;
      }

      async function startStream() {
        const status = document.getElementById('audio-status');
        if (!audioCtx) {
          audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 22050 });
        }
        if (audioCtx.state !== 'running') {
          await audioCtx.resume();
        }
        if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
          status.textContent = 'Stream already running';
          return;
        }
        const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
        ws = new WebSocket(`${protocol}://${location.host}/v1/conductor/audio/stream`);
        ws.binaryType = 'arraybuffer';
        pendingFrames = [];
        nextTime = audioCtx.currentTime + 0.25;
        ws.onopen = () => { status.textContent = 'Live stream connected'; };
        ws.onmessage = (event) => {
          const buf = event.data;
          if (!buf || buf.byteLength === 0) return;
          const samples = pcm16ToFloat32(buf);
          pendingFrames.push(samples);
          schedulePendingFrames();
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
        pendingFrames = [];
        if (audioCtx) {
          nextTime = audioCtx.currentTime;
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
