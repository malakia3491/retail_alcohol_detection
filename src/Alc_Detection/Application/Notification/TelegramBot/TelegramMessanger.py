from Alc_Detection.Application.Notification.Message import Message
from aiogram import Bot, Dispatcher, Router
from aiogram.types import BufferedInputFile

from Alc_Detection.Application.IncidentManagement.Interfaces.Messenger import Messenger

class TelegramMessenger(Messenger):
    def __init__(
        self,
        dispatcher: Dispatcher,
        bot: Bot,
        api_token: str,
        webhook_url: str,        
    ):
        self._dispatcher = dispatcher
        self._bot = bot
        self._api_token = api_token
        self._webhook_url = webhook_url

    @property
    def dispatcher(self) -> Dispatcher:
        return self._dispatcher
    
    @property
    def token(self) -> str:
        return self._api_token
    
    @property
    def webhook_url(self) -> str:
        return self._webhook_url
    
    async def send_to_user(
        self, 
        message: Message
    ):
        user_id: list[str] = message.user_ids[0]
        text: str = message.build()
        p_captrion, p_img_src = message.planogram_img
        r_captrion, r_img_src = message.realogram_img
        pass

    async def broadcast_message(
        self, 
        message: Message
    ):
        text: str = message.build()
        img_src = [message.planogram_img, message.realogram_img]
        
        media = []
        for caption, path in img_src:
            with open(path, "rb") as f:
                media.append(
                    InputMediaPhoto(
                        media=BufferedInputFile(
                            f.read(),
                            filename=caption
                        )
                    )
                )
        
        for chat_id in message.user_ids:
            try:
                await self._bot.send_message(chat_id, text)
            except Exception as ex:
                raise ex
            await self._bot.send_message(chat_id=chat_id, text=text)
            await self._bot.send_media_group(chat_id=chat_id, media=media)