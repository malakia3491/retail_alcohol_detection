import abc

class Messenger(abc.ABC):    
    
    @abc.abstractmethod
    def send(
        self,
        ids: list[str],
        message: str
    ) -> bool:
        pass