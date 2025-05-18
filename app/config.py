from pydantic_settings import BaseSettings, SettingsConfigDict


class RequestServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DATABASE_URL: str
    RABBITMQ_URL: str

    USER_SERVICE_URL: str
    USER_SERVICE_API_KEY: str

    HACKATHON_SERVICE_URL: str
    HACKATHON_SERVICE_API_KEY: str

    JWT_SECRET: str = "dstu"
    ROOT_PATH: str = ""


Settings = RequestServiceSettings()
