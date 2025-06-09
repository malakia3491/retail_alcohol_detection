from uuid import UUID
from jose import JWTError
from typing import Optional
from passlib.context import CryptContext

from Alc_Detection.Application.Auth.Exceptions import InactiveUserException, InvalidCredentialsException, InvalidTokenException
from Alc_Detection.Application.Auth.TokenService import TokenService
from Alc_Detection.Application.Requests.Models import AuthResponse, Permition, Person, Store, Shift, Post
from Alc_Detection.Application.StoreInformation.Services.StoreServiceFacade import StoreService
from Alc_Detection.Persistance.Repositories.PersonRepository import PersonRepository
from Alc_Detection.Persistance.Repositories.StoreRepository import StoreRepository

class AuthService:
    def __init__(
        self,
        store_serivce: StoreService,
        user_repository: PersonRepository,
        store_repository: StoreRepository,
        token_service: TokenService,
        pwd_context: CryptContext
    ):
        self._store_serivce = store_serivce
        self.user_repo = user_repository
        self._store_repo = store_repository
        self.token_service = token_service
        self.pwd_context = pwd_context

    async def authenticate(
        self, 
        email: str, 
        password: str
    ) -> Optional[AuthResponse]:
        """Аутентификация пользователя по логину и паролю"""
        user = await self.user_repo.find_by_email(email)
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
            store, shift, post = await self._store_serivce.get_work_place(user)
            if store:
                store_rep = Store(
                    id=store.id,
                    name=store.name,
                    is_office=store.is_office
                )
                shift_rep = Shift(
                    id=shift.id,
                    store_id=store.id,
                    work_time_start=shift.work_time.start,
                    work_time_end=shift.work_time.end,
                    break_time_start=shift.break_time.start,
                    break_time_end=shift.break_time.end,
                    name=shift.name,
                )
                post_response = Post(
                    id=post.id, 
                    name=post.name,
                    permitions=[Permition(id=permition.id, name=permition.name) for permition in post.permitions]
                )
            else:
                store_rep = None
                shift_rep = None 
                post_response = None
            return Person(
                id=user.id,
                telegram_id=user.telegram_id,
                name=user.name,
                email=user.email,
                store=store_rep,
                shift=shift_rep,
                post=post_response,
                is_store_worker=user.is_store_worker,
                is_active=user.is_active,
                access_token=token,
            )
        except (JWTError, ValueError) as e:
            raise InvalidTokenException("Could not validate credentials") from e
        
    async def register_store(
        self,
        login: str,
        password: str,
    ) -> Optional[AuthResponse]:
        """Регистрация нового магазина"""
        
        existing_store = await self._store_serivce.get_store_by_login(login)
        if not existing_store:
            raise InvalidCredentialsException("Store with this email does not exist")
        
        hashed_password = self.pwd_context.hash(password)
        
        data = {
            "login":login,
            "password_hash":hashed_password,
        }
        await self._store_repo.update(
            existing_store.id,
            data=data
        )
        
        return await self.authenticate(login, password) 
    
    async def store_authenticate(
        self, 
        login: str, 
        password: str
    ) -> Optional[AuthResponse]:
        """Аутентификация пользователя по логину и паролю"""
        store = await self._store_serivce.get_store_by_login(login)
        if not store or not self.pwd_context.verify(password, store.password_hash):
            raise InvalidCredentialsException("Invalid username or password")

        access_token = self.token_service.create_access_token(store)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=str(store.id),
        )
        
    async def store_me(self, token: str) -> Store:
        """Получение информации о текущем пользователе"""
        try:
            payload = self.token_service.verify_token(token)
            store_id = payload.get("sub")
            
            if not store_id:
                raise InvalidTokenException("Invalid token payload")
            
            store = await self._store_repo.get(UUID(store_id))

            return Store(
                id=store.id,
                name=store.name,
                is_office=store.is_office,
                login=store.login,
            )
        except (JWTError, ValueError) as e:
            raise InvalidTokenException("Could not validate credentials") from e