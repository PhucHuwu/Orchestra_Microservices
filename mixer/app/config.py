from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "mixer"
    exchange_name: str = Field(default="orchestra.events", alias="EXCHANGE_NAME")
    input_queue: str = Field(default="instrument.output", alias="INPUT_QUEUE")
    input_routing_key: str = Field(default="instrument.*.output", alias="INPUT_ROUTING_KEY")
    output_queue: str = Field(default="playback.output", alias="OUTPUT_QUEUE")
    output_routing_key: str = Field(default="playback.output", alias="OUTPUT_ROUTING_KEY")

    rabbitmq_url: str = Field(
        default="amqp://orchestra:orchestra@rabbitmq:5672/%2F", alias="RABBITMQ_URL"
    )
    prefetch_count: int = Field(default=50, alias="PREFETCH_COUNT")


settings = Settings()
