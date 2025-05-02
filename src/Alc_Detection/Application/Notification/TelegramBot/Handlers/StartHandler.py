from aiogram import Router, types

from Alc_Detection.Application.Notification.TelegramBot.Handlers.Handler import Handler

class StartHandler(Handler):
    def _register_handlers(self):
        self._router.register_message_handler(
            self.cmd_start,
            commands=['start'],
            state='*'
    )
    
    async def cmd_start(self, message: types.Message):
        await message.answer("Привет! Я бот без декораторов!")