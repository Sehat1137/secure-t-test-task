from pydantic import BaseSettings, Field


class PostgresConfig(BaseSettings):
    host: str
    port: int
    user: str
    db: str
    password: str

    class Config:
        env_prefix = "POSTGRES_"


class Config(BaseSettings):
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
