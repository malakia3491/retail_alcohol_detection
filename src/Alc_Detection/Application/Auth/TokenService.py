from datetime import datetime, timedelta
from jose import JWTError, jwt

from Alc_Detection.Application.Auth.Exceptions import InvalidTokenException
from Alc_Detection.Domain.Store.PersonManagment.Person import Person

class TokenService:
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire = access_token_expire_minutes

    def create_access_token(self, user: Person) -> str:
        expires_delta = timedelta(minutes=self._access_token_expire)
        expire = datetime.now() + expires_delta
        
        token_data = {
            "sub": str(user.id),
            "name": user.name,
            "is_store_worker": user.is_store_worker,
            "exp": expire
        }
        return jwt.encode(
            claims=token_data,
            key=self._secret_key,
            algorithm=self._algorithm
        )

    def verify_token(self, token: str) -> dict:
        """Валидирует токен и возвращает payload"""
        try:
            payload = jwt.decode(
                token=token,
                key=self._secret_key,
                algorithms=[self._algorithm]
            )
            if datetime.now() > datetime.fromtimestamp(payload["exp"]):
                raise InvalidTokenException("Token expired")
            return payload
        except JWTError as e:
            raise InvalidTokenException("Invalid token") from e