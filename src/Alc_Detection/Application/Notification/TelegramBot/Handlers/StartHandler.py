from aiogram import F, Router, types

from Alc_Detection.Application.Notification.TelegramBot.Handlers.Handler import Handler

class StartHandler(Handler):
    def __init__(self):
        super().__init__()
        self._register_handlers()
    
    def _register_handlers(self):
        self.router.message.register(
            self.cmd_start,
            F.text == '/start'
        )
    
    async def cmd_start(self, message: types.Message):
        await message.answer("Привет!\nДля получения уведомлений введтие команду /register")