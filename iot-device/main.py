import ujson
import utime
from machine import PWM, Pin
from umqtt.simple import MQTTClient

import config


def on_message(topic: bytes, msg: bytes) -> None:
    payload = ujson.loads(msg)
    pitch = int(payload.get("pitch", 0))
    duration = float(payload.get("duration", 0.1))
    volume = int(payload.get("volume", 20))
    play_tone(pitch, duration, volume)


def play_tone(pitch: int, duration: float, volume: int) -> None:
    pwm = PWM(Pin(config.BUZZER_PIN))
    pwm.freq(max(100, pitch * 10))
    pwm.duty_u16(min(65535, max(0, volume * 512)))
    utime.sleep(duration)
    pwm.deinit()


def main() -> None:
    while True:
        try:
            client = MQTTClient(
                client_id=config.MQTT_CLIENT_ID,
                server=config.MQTT_BROKER_HOST,
                port=config.MQTT_BROKER_PORT,
            )
            client.set_callback(on_message)
            client.connect()
            client.subscribe(config.MQTT_TOPIC)

            while True:
                client.wait_msg()
        except Exception:
            utime.sleep(2)


main()
