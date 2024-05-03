import pydantic
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str = pydantic.Field(alias="POSTGRES_USER")
    DB_PASSWORD: str = pydantic.Field(alias="POSTGRES_PASSWORD")
    DB_SERVER: str = pydantic.Field(alias="POSTGRES_HOST")
    DB_PORT: int = pydantic.Field(alias="POSTGRES_PORT")
    DB_NAME: str = pydantic.Field(alias="POSTGRES_DB_NAME")

    class Config:
        env_file = ".env"


settings = Settings() # type: ignore
CONN_TEMPLATE = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_SERVER}:{settings.DB_PORT}/{settings.DB_NAME}"
