from numpy import ndarray
from torch import Tensor
from torch.nn import Module

class DistanceClassifier(Module):
    def __init__(self):
        super(DistanceClassifier, self).__init__()    
        
    def forward(self, X: Tensor) -> ndarray:
        pass
    
    def fit(self, X: Tensor, Y: Tensor) -> str:
        pass
 
    def fine_fill(self, X: Tensor, Y: Tensor) -> str:
        pass
    
    def fill(self, X: Tensor, Y: Tensor) -> str:
        pass
    
    def evaluate(self, X: Tensor, Y: Tensor) -> dict[str, float]:
        pass
    
    def save(self, path: str) -> None:
        pass
    
    def load(self, path: str) -> None:
        pass