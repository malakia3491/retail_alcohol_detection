from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from Alc_Detection.Application.Notification.TelegramBot.Handlers.Handler import Handler
from Alc_Detection.Application.Notification.TelegramBot.States.RegistrationStates import RegistrationStates
from Alc_Detection.Persistance.Repositories.PersonRepository import PersonRepository

class RegistrationHandler(Handler):
    def __init__(
        self,
        person_repository: PersonRepository
    ):
        super().__init__()
        self._person_repository = person_repository
        self._register_handlers()
    
    def _register_handlers(self):
        self.router.message.register(
            self.cmd_start,
            F.text == '/register'
        )
        self.router.message.register(
            self.process_email,
            StateFilter(RegistrationStates.waiting_for_email)
        )

    async def cmd_start(self, message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        
        existing_user = await self._person_repository.find_by_telegram_id(user_id)
        if existing_user:
            await message.answer("Вы уже зарегистрированы!")
            return

        await message.answer(
            "Добро пожаловать! Для завершения регистрации введите ваш корпоративный email:"
        )
        await state.set_state(RegistrationStates.waiting_for_email)

    async def process_email(self, message: types.Message, state: FSMContext):
        email = message.text.strip()
        user_id = message.from_user.id

        if not self._validate_email(email):
            await message.answer("Неверный формат email. Попробуйте еще раз:")
            return

        try:
            user = await self._person_repository.find_by_email(email)
            user.telegram_id = str(user_id) 
            await self._person_repository.update(user.id, {"telegram_id": str(user_id)})
            
            await message.answer(
                "Регистрация завершена! Теперь вы будете получать уведомления."
            )
        except Exception as e:
            await message.answer("Ошибка регистрации. Попробуйте позже.")
        finally:
            await state.clear()

    def _validate_email(self, email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]