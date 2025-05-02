import numpy as np
import torch

from Alc_Detection.Domain.NetworkModels.EmbeddingModel import EmbeddingNetwork

class Embedding:
    def __init__(self, cords: list[float], model: EmbeddingNetwork, id=None):
        if cords is None or len(cords) != model.embedding_shape:
            raise ValueError(cords)        
        self._cords = cords
        self._model = model
        self.id = id

    @property
    def vector(self) -> np.ndarray:
        return self.to_np_array()
    
    @property
    def model(self) -> EmbeddingNetwork:
        return self._model
        
    def to_np_array(self) -> np.ndarray:
        return np.array(self._cords)
    
    def to_tensor(self) -> torch.Tensor:
        return torch.as_tensor(self._cords).float()
    
    def to_list(self) -> list[float]:
        return self._cords