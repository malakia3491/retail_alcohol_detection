import traceback
from jose import JWTError
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from Alc_Detection.Application.Auth.AuthService import AuthService
from Alc_Detection.Application.Requests.Models import AuthResponse, Person, Store

class AuthController:
    def __init__(self, 
                 auth_service: AuthService):
        self._auth_service = auth_service
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route("/login/", self.login, methods=["POST"], status_code=status.HTTP_200_OK)
        self.router.add_api_route("/me/", self.me, methods=["POST"], status_code=status.HTTP_200_OK)
        self.router.add_api_route("/store/login/", self.store_login, methods=["POST"], status_code=status.HTTP_200_OK)
        self.router.add_api_route("/store/me/", self.store_me, methods=["POST"], status_code=status.HTTP_200_OK)
        self.router.add_api_route("/store/register/", self.register_store, methods=["POST"], status_code=status.HTTP_200_OK)        
        
    async def login(
        self,
        request: OAuth2PasswordRequestForm = Depends()
    ) -> AuthResponse:
        print(request)
        response = await self._auth_service.authenticate(request.username, request.password)
        if not response:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        return response
    
    async def me(
        self,
        token: str = Form(...)
    ) -> Person:
        try:
            response = await self._auth_service.me(token)
            if response is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
            return response
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        
    async def register_store(
        self,
        request: OAuth2PasswordRequestForm = Depends()
    ) -> AuthResponse:
        response = await self._auth_service.register_store(request.username, request.password)
        if not response:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        return response
    
    async def store_login(
        self,
        request: OAuth2PasswordRequestForm = Depends()
    ) -> AuthResponse:
        response = await self._auth_service.store_authenticate(request.username, request.password)
        if not response:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        return response
    
    async def store_me(
        self,
        token: str = Form(...)
    ) -> Store:
        try:
            response = await self._auth_service.store_me(token)
            if response is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
            return response
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")