from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = Field(default="dashboard-api", alias="SERVICE_NAME")
    database_url: str = Field(
        default="postgresql+psycopg://orchestra:orchestra@postgres:5432/orchestra",
        alias="DATABASE_URL",
    )

    rabbitmq_url: str = Field(
        default="amqp://orchestra:orchestra@rabbitmq:5672/%2F",
        alias="RABBITMQ_URL",
    )
    rabbitmq_mgmt_api_url: str = Field(
        default="http://rabbitmq:15672/api",
        alias="RABBITMQ_MGMT_API_URL",
    )
    rabbitmq_mgmt_username: str | None = Field(default=None, alias="RABBITMQ_MGMT_USERNAME")
    rabbitmq_mgmt_password: str | None = Field(default=None, alias="RABBITMQ_MGMT_PASSWORD")

    exchange_name: str = Field(default="orchestra.events", alias="EXCHANGE_NAME")
    tempo_control_queue: str = Field(default="tempo.control", alias="TEMPO_CONTROL_QUEUE")
    playback_control_queue: str = Field(
        default="playback.control",
        alias="PLAYBACK_CONTROL_QUEUE",
    )

    metrics_stream_interval_seconds: float = Field(
        default=1.0, alias="METRICS_STREAM_INTERVAL_SECONDS"
    )
    snapshot_interval_seconds: float = Field(default=5.0, alias="SNAPSHOT_INTERVAL_SECONDS")
    rabbitmq_timeout_seconds: float = Field(default=2.0, alias="RABBITMQ_TIMEOUT_SECONDS")

    conductor_base_url: str = Field(default="http://conductor:8000", alias="CONDUCTOR_BASE_URL")
    score_storage_dir: str = Field(default="/shared-scores", alias="SCORE_STORAGE_DIR")
    audio_output_dir: str = Field(default="/shared-audio", alias="AUDIO_OUTPUT_DIR")
    audio_input_queue: str = Field(default="audio.render.input", alias="AUDIO_INPUT_QUEUE")
    audio_input_routing_key: str = Field(default="playback.output", alias="AUDIO_INPUT_ROUTING_KEY")
    audio_sample_rate: int = Field(default=22050, alias="AUDIO_SAMPLE_RATE")
    cors_allow_origins: str = Field(default="http://localhost:3000", alias="CORS_ALLOW_ORIGINS")


settings = Settings()
