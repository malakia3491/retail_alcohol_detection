import torch
import torch.nn as nn

from Alc_Detection.Application.VideoAnalytics.Classification.Models.EmbeddingModels.EmbeddingNet import EmbeddingNet

class SiameseNetwork(nn.Module):
    def __init__(self,
                 embedding_net: EmbeddingNet,
                 path="",
                 version=""):
        super(SiameseNetwork, self).__init__()
        self.embedding_net = embedding_net
        self.path=path
        self.version=version
        
    def forward(self, x1: torch.Tensor, x2: torch.Tensor, x3: torch.Tensor):
        anchor = self.embedding_net(x1)
        positive = self.embedding_net(x2)
        negative = self.embedding_net(x3)
        return anchor, positive, negative
    
    def get_embedding(self, X: torch.Tensor) -> torch.Tensor:
        X = X if isinstance(X, torch.Tensor) else torch.tensor(X)
        return self.embedding_net(X)