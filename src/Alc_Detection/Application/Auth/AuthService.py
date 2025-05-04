from typing import Optional
from uuid import UUID
from jose import JWTError
from passlib.context import CryptContext

from Alc_Detection.Application.Auth.Exceptions import InactiveUserException, InvalidCredentialsException, InvalidTokenException
from Alc_Detection.Application.Auth.TokenService import TokenService
from Alc_Detection.Application.Requests.Models import AuthResponse, Person
from Alc_Detection.Application.StoreInformation.Services.StoreService import StoreService
from Alc_Detection.Persistance.Repositories.PersonRepository import PersonRepository
from Alc_Detection.Persistance.Repositories.StoreRepository import StoreRepository

class AuthService:
    def __init__(
        self,
        store_service: StoreService,
        user_repository: PersonRepository,
        token_service: TokenService,
        pwd_context: CryptContext
    ):
        self._store_service = store_service
        self.user_repo = user_repository
        self.token_service = token_service
        self.pwd_context = pwd_context

    async def authenticate(
        self, 
        username: str, 
        password: str
    ) -> Optional[AuthResponse]:
        """Аутентификация пользователя по логину и паролю"""
        user = await self.user_repo.find_by_username(username)
        if not user or not self.pwd_context.verify(password, user.password_hash):
            raise InvalidCredentialsException("Invalid username or password")
        
        if not getattr(user, "is_active", True):
            raise InactiveUserException("User account is disabled")

        access_token = self.token_service.create_access_token(user)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=str(user.id),
        )

    async def me(self, token: str) -> Person:
        """Получение информации о текущем пользователе"""
        try:
            payload = self.token_service.verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise InvalidTokenException("Invalid token payload")
            
            user = await self.user_repo.get(UUID(user_id))
            store = self._store_service.get_work_place(user)
            return Person(
                id=user.id,
                telegram_id=user.telegram_id,
                name=user.name,
                is_worker=user.is_worker,
                is_active=user.is_active,
                access_token=token,
            )
        except (JWTError, ValueError) as e:
            raise InvalidTokenException("Could not validate credentials") from e