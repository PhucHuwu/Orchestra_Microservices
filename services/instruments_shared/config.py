from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class InstrumentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = Field(default="instrument-service", alias="SERVICE_NAME")
    instrument_name: str = Field(alias="INSTRUMENT_NAME")
    input_queue: str = Field(alias="INPUT_QUEUE")

    rabbitmq_url: str = Field(
        default="amqp://orchestra:orchestra@rabbitmq:5672/%2F",
        alias="RABBITMQ_URL",
    )
    exchange_name: str = Field(default="orchestra.events", alias="EXCHANGE_NAME")
    output_routing_key: str = Field(alias="OUTPUT_ROUTING_KEY")

    prefetch_count: int = Field(default=50, alias="PREFETCH_COUNT")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")


def default_output_routing_key(instrument_name: str) -> str:
    return f"instrument.{instrument_name}.output"
