from collections.abc import Callable
from typing import Any

from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import DeclarativeBase
from starlette.status import HTTP_403_FORBIDDEN

from .auth import get_user


class AccessController:
    def __init__(self, *roles: str):
        """
        Контроллер доступа для проверки ролей.

        :param hard_check: Включение жёсткой проверки ролей через внешний сервис.
        :param roles: Допустимые роли пользователя.
        """
        self.roles = roles

    def secure(self, dependency: Callable[..., Any]):
        """
        Создаёт функцию-зависимость для FastAPI с проверкой ролей.
        :param dependency: Зависимость, которую возвращаем при успешной проверке.
        :return: Зависимость с проверкой доступа.
        """

        async def wrapper(
            user: DeclarativeBase = Depends(get_user),  # Данные пользователя
            dep: Any = Depends(dependency),  # Оборачиваемая зависимость
        ) -> Any:
            """
            Обёртка для проверки доступа пользователя.
            :param user: Данные пользователя из get_user.
            :param dep: Возвращаемая зависимость.
            :return: Зависимость, если доступ разрешён.
            """
            user_role_names = {role.name for role in user.roles}
            if bool(user_role_names.intersection(set(self.roles))):
                return dep

            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You don't have the privileges to perform this action.",
            )

        return wrapper
