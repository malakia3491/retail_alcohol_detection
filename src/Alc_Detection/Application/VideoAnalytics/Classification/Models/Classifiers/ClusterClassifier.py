import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score, precision_score,
    recall_score, f1_score
)
from sklearn.cluster import (
    KMeans, DBSCAN, AgglomerativeClustering,
    SpectralClustering, Birch, MeanShift, OPTICS
)
from sklearn.metrics import pairwise_distances_argmin_min
from scipy.optimize import linear_sum_assignment

from Alc_Detection.Application.VideoAnalytics.Classification.Models.Classifiers.DistanceClassifier import DistanceClassifier

class ClusterClassifier(DistanceClassifier):
    def __init__(self, algorithm='kmeans', device='cpu', **kwargs):
        super(ClusterClassifier, self).__init__()
        self.models = {
            'kmeans': lambda: KMeans(**kwargs),
            'dbscan': lambda: DBSCAN(**kwargs),
            'agglomerative': lambda: AgglomerativeClustering(**kwargs),
            'spectral': lambda: SpectralClustering(**kwargs),
            'birch': lambda: Birch(**kwargs),
            'meanshift': lambda: MeanShift(**kwargs),
            'optics': lambda: OPTICS(**kwargs),
        }
        if algorithm not in self.models:
            raise ValueError(f"Алгоритм {algorithm} не поддерживается.")
        self.algorithm = algorithm
        self.device = device
        self.model = None
        self.cluster_centers_ = None
        self.cluster_indices = None
        self.mapping = None
        # хранение полных данных для дообучения
        self._X = None
        self._Y = None

    def fit(self, X: torch.Tensor, Y: torch.Tensor) -> None:
        """
        Обучение кластерного классификатора на всем наборе данных.
        X: torch.Tensor или np.ndarray [n_samples, dim]
        Y: torch.Tensor или np.ndarray [n_samples]
        """
        X_np = X.cpu().numpy() if isinstance(X, torch.Tensor) else X
        Y_np = Y.cpu().numpy() if isinstance(Y, torch.Tensor) else Y
        self._X = X_np
        self._Y = Y_np

        self.model = self.models[self.algorithm]()
        self.model.fit(self._X)
        self._update_centers_and_mapping()

    def add_classes(self, X_new: torch.Tensor, Y_new: torch.Tensor) -> None:
        """
        Добавление новых примеров и переобучение модели.
        """
        X_np = X_new.cpu().numpy() if isinstance(X_new, torch.Tensor) else X_new
        Y_np = Y_new.cpu().numpy() if isinstance(Y_new, torch.Tensor) else Y_new
        # объединяем старые и новые данные
        if self._X is None:
            self._X, self._Y = X_np, Y_np
        else:
            self._X = np.vstack([self._X, X_np])
            self._Y = np.concatenate([self._Y, Y_np])
        # переобучаем модель
        self.model = self.models[self.algorithm]()
        self.model.fit(self._X)
        self._update_centers_and_mapping()

    def _update_centers_and_mapping(self):
        """Вспомогательная функция для обновления центров кластеров и маппинга."""
        if hasattr(self.model, 'cluster_centers_'):
            self.cluster_centers_ = self.model.cluster_centers_
            self.cluster_indices = np.arange(self.cluster_centers_.shape[0])
            labels = self.model.predict(self._X)
        else:
            labels = self.model.labels_
            unique = np.unique(labels)
            self.cluster_centers_ = np.vstack([
                self._X[labels == c].mean(axis=0) for c in unique
            ])
            self.cluster_indices = unique
        # создаем соответствие кластер->класс
        self.mapping = self._match_clusters_majority(self._Y, labels)

    def forward(self, X: torch.Tensor) -> np.ndarray:
        if self.model is None:
            raise ValueError("Модель не обучена. Вызовите fit() или add_classes().")
        X_np = X.cpu().numpy() if isinstance(X, torch.Tensor) else X
        if hasattr(self.model, 'predict'):
            cluster_labels = self.model.predict(X_np)
        else:
            closest, _ = pairwise_distances_argmin_min(X_np, self.cluster_centers_)
            cluster_labels = np.array([self.cluster_indices[i] for i in closest])
        return np.array([self.mapping[c] for c in cluster_labels])

    def evaluate(self, X: torch.Tensor, Y: torch.Tensor) -> dict[str, float]:
        X_np = X.cpu().numpy() if isinstance(X, torch.Tensor) else X
        Y_np = Y.cpu().numpy() if isinstance(Y, torch.Tensor) else Y
        preds = self.forward(X)
        return {
            'Accuracy': accuracy_score(Y_np, preds),
            'Precision': precision_score(Y_np, preds, average='macro', zero_division=0),
            'Recall': recall_score(Y_np, preds, average='macro', zero_division=0),
            'F1': f1_score(Y_np, preds, average='macro', zero_division=0)
        }

    @staticmethod
    def _match_clusters_majority(true_labels, cluster_labels):
        label_map = {}
        for c in np.unique(cluster_labels):
            mask = cluster_labels == c
            most = np.bincount(true_labels[mask]).argmax()
            label_map[c] = most
        return label_map
