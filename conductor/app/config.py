from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "conductor"

    rabbitmq_url: str = Field(
        default="amqp://orchestra:orchestra@rabbitmq:5672/%2F", alias="RABBITMQ_URL"
    )
    exchange_name: str = Field(default="orchestra.events", alias="EXCHANGE_NAME")
    tempo_control_queue: str = Field(default="tempo.control", alias="TEMPO_CONTROL_QUEUE")
    heartbeat_queue: str = Field(default="system.heartbeat", alias="HEARTBEAT_QUEUE")

    score_dir: str = Field(default="scores", alias="SCORE_DIR")
    default_score_path: str = Field(
        default="Concierto-De-Aranjuez.mid",
        alias="DEFAULT_SCORE_PATH",
    )
    default_bpm: int = Field(default=96, alias="DEFAULT_BPM")
    heartbeat_interval_seconds: float = Field(default=1.0, alias="HEARTBEAT_INTERVAL_SECONDS")
    prefetch_count: int = Field(default=100, alias="PREFETCH_COUNT")

    guitar_service_url: str = Field(default="http://guitar-service:8000", alias="GUITAR_SERVICE_URL")
    oboe_service_url: str = Field(default="http://oboe-service:8000", alias="OBOE_SERVICE_URL")
    drums_service_url: str = Field(default="http://drums-service:8000", alias="DRUMS_SERVICE_URL")
    mixer_service_url: str = Field(default="http://mixer:8000", alias="MIXER_SERVICE_URL")
    dashboard_api_url: str = Field(default="http://dashboard-api:8000", alias="DASHBOARD_API_URL")
    soundfont_path: str = Field(default="/usr/share/sounds/sf2/FluidR3_GM.sf2", alias="SOUNDFONT_PATH")
    audio_sample_rate: int = Field(default=22050, alias="AUDIO_SAMPLE_RATE")


settings = Settings()
