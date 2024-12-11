from collections.abc import Callable
from functools import cached_property
from typing import Any

import pytz
from pydantic_settings import BaseSettings
from .abstract import TokenControllerAbstract, UserRepositoryAbstract
from ._globals import ctx


class InitJWTAuth(BaseSettings):
    tokens_controller: Callable[[], TokenControllerAbstract]
    user_repository: Callable[[], UserRepositoryAbstract] | None = None
    TIMEZONE: str = "UTC"
    jwt: BaseSettings

    def __init__(self, **values: Any):
        super().__init__(**values)
        ctx.settings = self

    @cached_property
    def timezone(self):
        return pytz.timezone(self.TIMEZONE)
