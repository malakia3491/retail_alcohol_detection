from aiogram import Router

class Handler:
    def __init__(self):
        self._router = Router()
        
    @property
    def router(self) -> Router:
        return self._router