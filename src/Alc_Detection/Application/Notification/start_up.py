from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from Alc_Detection.Application.Notification.TelegramBot.Handlers.Handler import Handler
from Alc_Detection.Application.Notification.TelegramBot.Handlers.StartHandler import StartHandler
from Alc_Detection.Application.Notification.TelegramBot.TelegramMessanger import TelegramMessenger

from Alc_Detection.Persistance.Configs.ConfigReader import IniConfigReader

class TelegramInitializer:
    def __init__(
        self,
        config_reader: IniConfigReader
    ):
        self._config_reader = config_reader
        
    async def initialize(self):
        main_router = Router()
        handlers = self._initialize_handlers()
        for handler in handlers:            
            main_router.include_router(handler.router)
        token = self._config_reader.get_tg_api_key()    
        url = self._config_reader.get_webhook_url()
        bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await bot.set_webhook(url)        
        dp = Dispatcher(storage=MemoryStorage())
        messanger = TelegramMessenger(
            dispatcher=dp,
            bot=bot,
            api_token=token,
            webhook_url=url
        )
        return messanger
        
    def _initialize_handlers(self) -> list[Handler]:
        start_handler = StartHandler()
        handlers = [start_handler]
        return handlers