import abc
from torch import Tensor
from ultralytics.engine.results import Results 

class BottlesDetectionService(abc.ABC):
    @abc.abstractmethod
    def detect_bottles_on(self, processed_img: Tensor) -> Results:
        pass
    
class PersonsDetectionService(abc.ABC):
    @abc.abstractmethod
    def detect_persons_on(self, processed_img: Tensor) -> bool:
        pass