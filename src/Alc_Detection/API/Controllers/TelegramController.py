from fastapi import APIRouter, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update

from Alc_Detection.Application.Notification.TelegramBot.TelegramMessanger import TelegramMessenger

class TelegramBotContoller:
    def __init__(self, 
                 messenger: TelegramMessenger):
        self._messenger = messenger
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(f"",
                                  self.telegram_webhook,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        
    async def telegram_webhook(
        self,
        req: Request
    ) -> Response:
        data = await req.json()
        return await self._messenger.process(Update(**data))