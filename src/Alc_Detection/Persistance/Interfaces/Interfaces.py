import abc

class ConfigReader(abc.ABC):
    @abc.abstractmethod
    def get_db_connection(self) -> str:
        pass