from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "dashboard-api"
    database_url: str = "postgresql+psycopg://orchestra:orchestra@postgres:5432/orchestra"


settings = Settings()
