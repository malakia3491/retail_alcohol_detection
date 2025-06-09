from video_control.application.API.ApiRequester import ApiRequester
from video_control.application.conf.Config import Config
from video_control.domain.Store import Store

class AuthService:
    def __init__(self, requester: ApiRequester, config: Config):
        self._requester = requester
        self._config = config 
        self._store = None
        
    @property
    def is_logined(self):
        return not self._store.code is None 
    
    async def on_start(self) -> 'AuthService':
        if self._config.is_stored_data:
            store = Store.from_dict(
                id=self._config.id,
                address=self._config.address,
                name=self._config.name,
                code=self._config.code
            )        
        elif self._requester.ready and self._config.is_filled:
            store = await self.login(
                username=self._config.login,
                password=self._config.password
            )
        self._store = store
        print('AuthService: initialized')
        return self
            
    async def login(self, username: str, password: str):
        if not username or not password:
            raise ValueError("Username and password must be provided")                
        
        data = await self._requester.login(username, password) 
        store = await self.me(data.get("access_token"))
        self._store = store
        return store        
    
    async def me(self, token: str):
        data = await self._requester.me(token=token)
        store = Store(
            id=data.get("id"),
            name=data.get("name"),
            address=data.get("store_address"),
            code=token
        )
        self._store = store
        return store