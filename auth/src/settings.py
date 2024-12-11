from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='JWT_',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    ACCESS_KEY: str = ''
    ACCESS_EXPIRE: float = 30.0

    REFRESH_KEY: str = ''
    REFRESH_EXPIRE: float = 60.0 * 24

    ALGORITHM: str = 'HS256'


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='REDIS_',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    host: str = 'localhost'
    port: int = 6379
    default_db: int = 0
    token_db: int = 1
    decode_responses: bool = True


class PgSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='POSTGRES_',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    host: str = 'localhost'
    port: int = 5432
    dbname: str = Field(alias='POSTGRES_DB')
    user: str = ''
    password: str = ''

    @cached_property
    def get_postgres_url(self) -> URL:
        user = self.user
        password = self.password
        host = self.host
        port = self.port
        dbname = self.dbname
        return URL(
            drivername='postgresql+asyncpg',
            username=user,
            password=password,
            host=host,
            port=port,
            database=dbname,
            query={},  # type: ignore
        )


class Settings(BaseSettings):
    redis: RedisSettings = RedisSettings()
    postgres: PgSettings = PgSettings()
    SALT: str = ''


settings = Settings()
