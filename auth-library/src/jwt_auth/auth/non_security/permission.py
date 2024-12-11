from typing import Callable, Any
from fastapi import Depends, HTTPException, Request
from starlette.status import HTTP_403_FORBIDDEN

from .auth import get_user
from ...utils.check_role_request import get_roles


class AccessController:
    def __init__(self, hard_check: bool, *roles: str):
        """
        Контроллер доступа для проверки ролей.

        :param hard_check: Включение жёсткой проверки ролей через внешний сервис.
        :param roles: Допустимые роли пользователя.
        """
        self.hard_check = hard_check
        self.roles = roles

    def secure(self, dependency: Callable[..., Any]):
        """
        Создаёт функцию-зависимость для FastAPI с проверкой ролей.
        :param dependency: Зависимость, которую возвращаем при успешной проверке.
        :return: Зависимость с проверкой доступа.
        """

        async def wrapper(
            request: Request,  # HTTP-запрос
            payload: dict = Depends(get_user),  # Данные пользователя
            dep: Any = Depends(dependency),  # Оборачиваемая зависимость
        ) -> Any:
            """
            Обёртка для проверки доступа пользователя.
            :param payload: Данные пользователя из get_user.
            :param request: Запрос.
            :param dep: Возвращаемая зависимость.
            :return: Зависимость, если доступ разрешён.
            """
            if not self.hard_check:
                user_roles = payload.get("roles", [])


                has_permission = any(role in user_roles for role in self.roles)
            else:
                roles_from_service = await get_roles(
                    user_id=payload["sub"], headers=dict(request.headers)
                )
                roles_names = [role['name'] for role in roles_from_service]

                has_permission = any(role in roles_names for role in self.roles)

            if has_permission:
                return dep  # Возвращаем зависимость, если проверка успешна

            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You don't have the privileges to perform this action.",
            )

        return wrapper
