from typing import Optional

from auth.models import User
from auth.utils import get_user_db
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas

SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    Класс для управления операциями пользователей с использованием BaseUserManager.

    Атрибуты:
    reset_password_token_secret: Секретный ключ для сброса паролей.
    verification_token_secret: Секретный ключ для подтверждения пользователей.
    """

    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Метод, вызываемый после регистрации пользователя.

        Выводит сообщение о том, что пользователь зарегистрировался.

        Параметры:
        user (User): Пользователь, который зарегистрировался.
        request (Optional[Request]): Объект запроса (необязательно).
        """
        print(f'Пользователь {user.id} зарегистрирован.')

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        """
        Метод для создания нового пользователя.

        Проверяет пароль, проверяет, существует ли пользователь, создает словарь пользователя,
        хэширует пароль, устанавливает идентификатор роли, создает пользователя в базе данных, вызывает
        метод on_after_register и возвращает созданного пользователя.

        Параметры:
        user_create (schemas.UC): Данные пользователя для создания.
        safe (bool): Флаг, указывающий, следует ли создавать безопасный словарь пользователя (необязательно, по умолчанию False).
        request (Optional[Request]): Объект запроса (необязательно).

        Возвращает:
        models.UP: Созданный пользователь.
        """
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["role_id"] = 1

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
