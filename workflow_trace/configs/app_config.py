from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WORKFLOW_TRACE_",
        extra="ignore",
    )

    service_port: int = 7890
    es_url: str = "http://127.0.0.1:9200"
    es_index: str = "spark-agent-builder-*"
    es_username: str = ""
    es_password: str = ""
    es_verify: bool = True
    es_timeout_seconds: int = 10


settings = Settings()
