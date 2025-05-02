import abc

from Alc_Detection.Application.Notification.Message import Message

class Messenger(abc.ABC):    
    
    @abc.abstractmethod
    async def send_to_user(self, message: Message):
        pass

    @abc.abstractmethod
    async def broadcast_message(self, message: Message):
        pass