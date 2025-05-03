from fastapi import APIRouter, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update

class TelegramBotContoller:
    def __init__(self, 
                 api_token: str,
                 dispetcher: Dispatcher):
        self._token = api_token
        self._dispetcher = dispetcher
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(f"/{self._token}",
                                  self.telegram_webhook,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        
    async def telegram_webhook(
        self,
        req: Request
    ) -> Response:
        data = await req.json()
        update = Update(**data)
        
        await self._dispetcher.process_update(update)
        
        return Response(status_code=200)