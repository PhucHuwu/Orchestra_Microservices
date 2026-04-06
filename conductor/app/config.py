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
    heartbeat_interval_seconds: float = Field(default=1.0, alias="HEARTBEAT_INTERVAL_SECONDS")
    prefetch_count: int = Field(default=100, alias="PREFETCH_COUNT")


settings = Settings()
