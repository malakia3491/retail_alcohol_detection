
from Alc_Detection.Application.IncidentManagement.Interfaces.Messenger import Messenger


class TelegramMessenger(Messenger):
    def __init__(
        self
    ):
        pass
    
    def send(
        self,
        ids: list[str],
        message: str
    ) -> bool:
        pass