import numpy as np
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score
)
import torch
from Alc_Detection.Application.VideoAnalytics.Classification.Models.Classifiers.DistanceClassifier import DistanceClassifier

from sklearn.cluster import (
    KMeans, 
    DBSCAN, 
    AgglomerativeClustering, 
    SpectralClustering, 
    Birch, 
    MeanShift, 
    OPTICS
)
from sklearn.metrics import pairwise_distances_argmin_min
from scipy.optimize import linear_sum_assignment

class ClusterClassifier(DistanceClassifier):
    def __init__(self, algorithm='kmeans', **kwargs):
        super(ClusterClassifier, self).__init__()
        self.models = self.__init_models_dic()
        if algorithm not in self.models.keys():
            raise ValueError(f"Алгоритм {algorithm} не поддерживается.")
        self.algorithm = algorithm
        self.kwargs = kwargs
        self.model = None
        self.cluster_centers_ = None
        self.cluster_indices = None
        self.mapping = None

    def __init_models_dic(self):
        models = {
            "kmeans": lambda kwargs: KMeans(**kwargs),
            "dbscan": lambda kwargs: DBSCAN(**kwargs),
            "agglomerative": lambda kwargs: AgglomerativeClustering(**kwargs),
            "spectral": lambda kwargs: SpectralClustering(**kwargs),
            "birch": lambda kwargs: Birch(**kwargs),
            "meanshift": lambda kwargs: MeanShift(**kwargs),
            "optics": lambda kwargs: OPTICS(**kwargs)
        }
        return models

    def __match_clusters(self, true_labels, cluster_labels):
        """
        Устанавливает соответствие между предсказанными кластерами и истинными метками классов.
        Возвращает:
            cluster_to_class (dict): Словарь соответствий {кластер -> класс}.
            new_cluster_labels (array): Преобразованные кластеры с заменой номеров на классы.
        """
        unique_true = np.unique(true_labels)
        unique_clusters = np.unique(cluster_labels)

        matrix = np.zeros((len(unique_true), len(unique_clusters)), dtype=int)
        for true, pred in zip(true_labels, cluster_labels):
            true_idx = np.where(unique_true == true)[0][0]
            pred_idx = np.where(unique_clusters == pred)[0][0]
            matrix[true_idx, pred_idx] += 1

        row_ind, col_ind = linear_sum_assignment(matrix, maximize=True)

        cluster_to_class = {unique_clusters[col]: unique_true[row] for row, col in zip(row_ind, col_ind)}

        new_cluster_labels = np.array([cluster_to_class[pred] for pred in cluster_labels])
        return cluster_to_class, new_cluster_labels
    
    def __match_clusters_majority(self, true_labels, cluster_labels):
        label_map = {}
        unique_clusters = np.unique(cluster_labels)
        for cluster in unique_clusters:
            mask = (cluster_labels == cluster)
            cluster_true_labels = true_labels[mask]
            most_common = np.bincount(cluster_true_labels).argmax()
            label_map[cluster] = most_common
        return label_map

    def fit(self, X: torch.Tensor, Y: torch.Tensor) -> None:
        X = X.cpu().numpy()
        Y = Y.cpu().numpy()
        
        self.model = self.models[self.algorithm](self.kwargs)
        self.model.fit(X)

        if hasattr(self.model, 'cluster_centers_'):
            self.cluster_centers_ = self.model.cluster_centers_
            self.cluster_indices = np.arange(self.cluster_centers_.shape[0])
        else:
            labels = self.model.labels_
            unique_clusters = np.unique(labels)
            self.cluster_centers_ = np.array([X[labels == i].mean(axis=0) for i in unique_clusters])
            self.cluster_indices = unique_clusters

        self.mapping = self.__match_clusters_majority(Y, self.model.labels_)

    def forward(self, X: torch.Tensor) -> np.ndarray:
        if self.model is None:
            raise ValueError("Модель не была обучена. Сначала вызовите метод fit().")
        
        X = X.cpu().numpy()
        
        if hasattr(self.model, 'predict'):
            predicted_labels = self.model.predict(X)
        else:
            closest, _ = pairwise_distances_argmin_min(X, self.cluster_centers_)
            predicted_labels = np.array([self.cluster_indices[i] for i in closest])
        
        return np.array([self.mapping[label] for label in predicted_labels])

    def evaluate(self, X: torch.Tensor, Y: torch.Tensor) -> dict[str, float]:
        if len(X) != len(Y):
            raise ValueError(f"Количество векторов X {len(X)} не соответствует количеству меток Y {len(Y)}!")
        if self.model is None:
            raise ValueError("Модель не была обучена!")
        
        X = X.cpu().numpy()
        Y = Y.cpu().numpy()
        
        predicted_labels = self(X)
        metrics = {
            'Accuracy': accuracy_score(Y, predicted_labels),
            'Precision': precision_score(Y, predicted_labels, average='macro', zero_division=0),
            'Recall': recall_score(Y, predicted_labels, average='macro', zero_division=0),
            'F1': f1_score(Y, predicted_labels, average='macro', zero_division=0)
        }
        return metrics
