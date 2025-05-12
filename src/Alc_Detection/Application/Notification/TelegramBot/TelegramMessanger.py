from fastapi import Response, status
from Alc_Detection.Application.Notification.Message import Message
from aiogram import Bot, Dispatcher
from aiogram import Bot
from aiogram.types import InputFile, InputMediaPhoto
from aiogram.types import FSInputFile 

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
    
    async def process(self, update) -> Response:
        try:
            await self.dispatcher.feed_update(self._bot, update)
            return Response(status_code=status.HTTP_200_OK)
        except Exception as ex:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def send_to_user(
        self, 
        message: Message
    ):
        user_id: list[str] = message.user_ids[0]
        text: str = message.build()

        pass

    async def broadcast_message(self, message: Message):
        text = message.build()

        base_path = r'C:\Users\pyatk\Desktop\Nikita\source\retail_alcohol_detection\src\Alc_Detection\Persistance\Images\Planograms\\'
        base_path2 = r'C:\Users\pyatk\Desktop\Nikita\source\retail_alcohol_detection\src\Alc_Detection\Persistance\Images\Realograms\\'
        p_caption = message.planogram_img[0]
        p_img_src = base_path + message.planogram_img[1]
        r_caption = message.realogram_img[0]
        r_img_src = base_path2 + message.realogram_img[1]
        media = [
            InputMediaPhoto(media=FSInputFile(path=p_img_src), caption=p_caption),
            InputMediaPhoto(media=FSInputFile(path=r_img_src), caption=r_caption),
        ]
        for chat_id in message.user_ids:
            try:
                await self._bot.send_message(chat_id=chat_id, text=text)
                await self._bot.send_media_group(chat_id=chat_id, media=media)
            except Exception as ex:
                print(f"Error sending to {chat_id}: {ex}")
                continue