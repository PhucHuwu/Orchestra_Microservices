# IoT Playback Service (ESP32)

This folder contains MicroPython skeleton code for ESP32 playback.

## Baseline behavior

- Connect WiFi
- Connect RabbitMQ MQTT plugin
- Subscribe topic: `playback.output`
- Parse event payload (`pitch`, `duration`, `volume`)
- Trigger buzzer/speaker playback
- Auto reconnect on WiFi/MQTT failure
