# Dashboard Frontend

Dashboard Frontend la Next.js app cho demo van hanh Orchestra Microservices, gom 4 man hinh bat buoc: Playback, Tempo, Monitoring, Fault Demo.

## Required environment variables

- `NEXT_PUBLIC_API_BASE_URL` (default: `http://localhost:8000`)
- `NEXT_PUBLIC_WS_URL` (default: `ws://localhost:8000/ws/metrics`)
- `NEXT_PUBLIC_FAULT_API_BASE_URL` (optional, chi can khi backend da mo fault API)

## Run local

```bash
npm install
npm run dev
```

Default UI URL: `http://localhost:3000`

## Scripts

- `npm run dev`: run local dev server
- `npm run test`: run unit/component tests with Vitest
- `npm run lint`: run Next.js ESLint checks
- `npm run build`: create production build

## Screen structure

- `/playback`
  - score selector + initial BPM input
  - start/stop playback session
  - running/stopped/failed session state
- `/tempo`
  - BPM slider + numeric input
  - apply BPM command
  - current BPM + latest update time
  - block command when no running session
- `/monitoring`
  - `GET /api/v1/metrics/overview`
  - `GET /api/v1/services/health`
  - `WS /ws/metrics` realtime stream
  - queue depth, consumer count, message rate, health, latency, socket state
  - realtime charts with Recharts
- `/fault-demo`
  - fault scenario triggers (run/cleanup)
  - timeline of demo events

## Smoke test checklist before demo

- [ ] Frontend load thanh cong tai `http://localhost:3000`
- [ ] Start playback tra ve session running, UI update trang thai
- [ ] Stop playback thanh cong, session ve stopped
- [ ] Tempo command bi chan khi chua co session running
- [ ] Tempo command accepted khi session dang running
- [ ] Monitoring hien queue depth / consumer count / message rate
- [ ] WebSocket state chuyen connected/disconnected/reconnecting dung thuc te
- [ ] Fault demo trigger tao event trong timeline
- [ ] `npm run test` pass
- [ ] `npm run lint` pass
- [ ] `npm run build` pass
