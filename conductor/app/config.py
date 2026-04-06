from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "conductor"
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672


settings = Settings()
