import torch
from numpy import ndarray
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from torch.nn.functional import cosine_similarity

from Alc_Detection.Application.VideoAnalytics.Classification.Models.Classifiers.DistanceClassifier import DistanceClassifier

class PrototypeClassifier(DistanceClassifier):
    def __init__(self, device, metric="euclidean"):
        super(DistanceClassifier, self).__init__()
        self.metrics = self._init_metrics_dict()
        if metric not in self.metrics:
            raise ValueError("Unsupported metric!")
        self.metric = metric
        self.device = device
        
        self.prototype_dict = {} 
    
    def _init_metrics_dict(self):
        return {
            "euclidean": lambda x, proto: torch.cdist(x, proto),
            "cosine": lambda x, proto: 1 - torch.mm(
                torch.nn.functional.normalize(x, p=2, dim=1),
                torch.nn.functional.normalize(proto, p=2, dim=1).T
            )
        }
                        # 1 - cosine_similarity(
                        #                 x.unsqueeze(1),  # (batch_size, 1, features)
                        #                 proto.unsqueeze(0),  # (1, n_prototypes, features)
                        #                 dim=2  # Сравниваем по оси features
                        #             )
        
    def to(self, device):
        self.device = device
        for label in self.prototype_dict:
            self.prototype_dict[label] = self.prototype_dict[label].to(device)
        return self
    
    def forward(self, x: torch.Tensor) -> ndarray:
        if not self.prototype_dict:
            raise ValueError("Classifier not trained!")
        
        x = x if isinstance(x, torch.Tensor) else torch.tensor(x, dtype=torch.float32)
        if x.dim() == 1:
            x = x.unsqueeze(0)
        
        labels = sorted(self.prototype_dict.keys())
        prototypes = torch.stack([self.prototype_dict[label] for label in labels])
        
        distances = self.metrics[self.metric](x, prototypes)
        _, min_indices = torch.min(distances, dim=1)
        
        labels_tensor = torch.tensor(labels, device=x.device)
        return labels_tensor[min_indices].cpu().numpy()
    
    def fine_fill(self, X: torch.Tensor, Y: torch.Tensor) -> str:
        if len(X) != len(Y):
            raise ValueError(f"X/Y size mismatch: {len(X)} vs {len(Y)}")        
        
        X = X.to(self.device) if isinstance(X, torch.Tensor) else torch.tensor(X, device=self.device).float()
        Y = Y.to(self.device) if isinstance(Y, torch.Tensor) else torch.tensor(Y, device=self.device).long() 
        
        for prototype, label in zip(X, Y):
            if label in self.prototype_dict:
                raise ValueError(label)
            self.prototype_dict[label] = prototype
            
        return f"Trained {self.__class__.__name__}. " + \
              f"Prototypes: {len(self.prototype_dict)}"
        
    def fill(self, X: torch.Tensor, Y: torch.Tensor) -> str:    
        if len(X) != len(Y):
            raise ValueError(f"X/Y size mismatch: {len(X)} vs {len(Y)}")
        
        X = X.to(self.device) if isinstance(X, torch.Tensor) else torch.tensor(X, device=self.device).float()
        Y = Y.to(self.device) if isinstance(Y, torch.Tensor) else torch.tensor(Y, device=self.device).long()
        
        self.prototype_dict.clear()  

        for prototype, label in zip(X, Y):
            self.prototype_dict[label] = prototype
        
        return f"Trained {self.__class__.__name__}. " + \
              f"Prototypes: {len(self.prototype_dict)}"
    
    def fit(self, X: torch.Tensor, Y: torch.Tensor) -> str:
        if len(X) != len(Y):
            raise ValueError(f"X/Y size mismatch: {len(X)} vs {len(Y)}")
        
        X = X.to(self.device) if isinstance(X, torch.Tensor) else torch.tensor(X, device=self.device).float()
        Y = Y.to(self.device) if isinstance(Y, torch.Tensor) else torch.tensor(Y, device=self.device).long()
        
        embeddings_dict = {}
        self.prototype_dict.clear()
        
        for x, y in zip(X, Y):
            label = y.item()
            if label not in embeddings_dict:
                embeddings_dict[label] = []
            embeddings_dict[label].append(x)

        for label, embeddings in embeddings_dict.items():
            stacked = torch.stack(embeddings).to(self.device)
            self.prototype_dict[label] = stacked.mean(dim=0)
        
        return f"Trained {self.__class__.__name__}. " + \
              f"Prototypes: {len(self.prototype_dict)}"
    
    def evaluate(self, X: torch.Tensor, Y: torch.Tensor) -> dict[str, float]:
        if len(X) != len(Y):
            raise ValueError(f"X/Y size mismatch: {len(X)} vs {len(Y)}")
        
        X = X.cpu().numpy()
        Y = Y.cpu().numpy()
        
        with torch.no_grad():
            preds = self(X)
        
        return {
            'Accuracy': accuracy_score(Y, preds),
            'Precision': precision_score(Y, preds, average='macro', zero_division=0),
            'Recall': recall_score(Y, preds, average='macro', zero_division=0),
            'F1': f1_score(Y, preds, average='macro', zero_division=0)
        }
    
    def save(self, path) -> None:
        torch.save({
            'prototype_dict': self.prototype_dict,
            'metric': self.metric
        }, path)
    
    def load(self, path) -> None:
        checkpoint = torch.load(path)
        self.metric = checkpoint['metric']     
        self.prototype_dict = checkpoint['prototype_dict']