from fastapi import UploadFile
import numpy as np
from torch import Tensor
import torch

import matplotlib.pyplot as plt
import numpy as np
from sklearn.manifold import TSNE
import umap
from typing import List

from Alc_Detection.Domain.Entities import *
from Alc_Detection.Domain.NetworkModels.EmbeddingModel import EmbeddingNetwork
from Alc_Detection.Application.VideoAnalytics.Interfaces.Classification import ClassificationService
from Alc_Detection.Application.VideoAnalytics.ImageProcessing.ImagePreprocessor import ImagePreprocessor
from Alc_Detection.Application.VideoAnalytics.Classification.Models.Classifiers.DistanceClassifier import DistanceClassifier
from Alc_Detection.Application.VideoAnalytics.Classification.Models.EmbeddingModels.EmbeddingNet import EmbeddingNet
from Alc_Detection.Application.VideoAnalytics.Classification.Models.EmbeddingModels.SiameseNetwork import SiameseNetwork
from Alc_Detection.Persistance.Cache.CacheBase import CacheBase

class BottleClassifierService(ClassificationService):
    def __init__(self,
                 preprocessor: ImagePreprocessor,
                 classifier: DistanceClassifier,
                 siamese_model: SiameseNetwork,
                 cache: CacheBase,
                 device: str,
    ):
        self._preprocessor = preprocessor
        self._classifier = classifier
        self._siamese_model = siamese_model
        self._model = EmbeddingNetwork(path=siamese_model.path,
                                       version=siamese_model.version)
        self._device = device
        self._cache = cache
    
    def on_start(self, products: list[Product]) -> None:
        self.load_classes(products)
    
    @property
    def model(self):
        return self._model
 
    async def classificate(self, 
                     img,
                     product_matrix: ProductMatrix) -> ProductMatrix:
        product_matrix = product_matrix.copy()
        for id, shelf in product_matrix:
            crops = await self.extract_crops(image=img,
                                             boxes=shelf.boxes)
            embeddings = self.get_embeddings_from(crops)
            labels = self._classifier(embeddings)
            shelf.set_products(self.convert_labels_to_products(labels))
        return product_matrix
    
    def convert_labels_to_products(self, labels: list[int]) -> list[Product]:
        return [self._cache.get(label) for label in labels]
    
    def load_classes(self, products: list[Product]):
        prototypes, labels = self.__products_to_data(products, self._model.version)
        if not None in prototypes:
            try:            
                self._classifier.fill(X=prototypes,
                                      Y=labels)
                for product in products:
                    self._cache.put(product.label, product)
            except Exception as ex:
                raise ex
    
    def add_classes(self, products: list[Product]):
        try: 
            prototypes, labels = self.__products_to_data(products, self._model.version)
            if len(prototypes) != 0 and len(labels) != 0 and len(prototypes) == len(labels):
                self._classifier.fine_fill(X=prototypes,
                                           Y=labels)
                for product in products:
                    self._cache.put(product.label, product)
        except Exception as ex:
            raise ex       
        
    async def preprocess(self, image_files: list[UploadFile]) -> list[np.ndarray]:
        crops = []
        for img_file in image_files:            
            img = await self._preprocessor.process(img_file) 
            crops.append(img.squeeze(0))
        batch = torch.stack(crops).to(self._device)
        return batch
    
    def get_embeddings_from(self, crops: np.ndarray) -> np.ndarray:
        self._siamese_model.eval()
        with torch.no_grad():
            embeddings = self._siamese_model.get_embedding(crops)
        return embeddings
    
    async def extract_crops(
        self,
        image: torch.Tensor,
        boxes: list[ProductBox]
    ) -> torch.Tensor:
            """
            Подготавливает тензор для классификационной модели
            :param image: BGR image (H, W, 3)
            :param boxes: Список ProductBox с координатами
            :return: Тензор в формате [N, C, H, W] на нужном устройстве
            """
            image = image.squeeze(0).permute(1, 2, 0)
            crops = []
            for box in boxes:
                if box.is_empty: continue 
                x1 = int(box.p_min.x)
                y1 = int(box.p_min.y)
                x2 = int(box.p_max.x)
                y2 = int(box.p_max.y)
                
                if x1 >= x2 or y1 >= y2: continue 
                
                crop = image[y1:y2, x1:x2, :]
                transformed_crop = await self._preprocessor.process(crop.cpu().numpy(), with_read=False)
                crops.append(transformed_crop)         
            if not crops:
                return torch.empty(0)
            
            first_shape = crops[0].shape
            if not all(crop.shape == first_shape for crop in crops):
                raise ValueError("Все обрезки должны иметь одинаковый размер")
            
            batch = torch.stack(crops).to(self._device)
            return batch
            
    def __products_to_data(self,
                           products: list[Product],
                           version: str
    ) -> tuple[np.ndarray[np.ndarray], np.ndarray]:
        labels = []
        prototypes = []
        for product in products:
            if product.is_classificated:
                prototypes.append(product.get_prototype(version))        
                labels.append(product.label)
            else: continue
        return np.array(prototypes), np.array(labels)

    def visualize_embeddings(
        self,
        products: List[Product],
        reduction_method: str = 'umap',
        figsize: tuple = (12, 8)
    ) -> None:
        """
        Визуализирует эмбеддинги и прототипы продуктов в 2D пространстве.
        """
        version = self._model.version
        all_embeddings = []
        prototypes = []
        labels = []
        colors = []
        unique_names = list({p.name for p in products})
        cmap = plt.get_cmap('tab20')
        color_map = {name: cmap(i/len(unique_names)) for i, name in enumerate(unique_names)}
        
        expected_dim = None  # Ожидаемая размерность эмбеддингов
        
        for product in products:
            try:
                # Получаем прототип и проверяем его размерность
                proto = product.get_prototype(version)
                if proto is None:
                    continue
                    
                if expected_dim is None:
                    expected_dim = proto.shape[0]
                elif proto.shape[0] != expected_dim:
                    print(f"Прототип {product.name} имеет несовместимую размерность: {proto.shape}")
                    continue
                    
                prototypes.append(proto)
                labels.append(f"Proto: {product.name}")
                colors.append(color_map[product.name])
                
                # Собираем эмбеддинги с проверкой размерности
                for img in product._images:
                    for emb in img.embeddings:
                        if emb.model.version == version:
                            emb_vector = emb.vector
                            if emb_vector.shape[0] != expected_dim:
                                print(f"Эмбеддинг продукта {product.name} имеет несовместимую размерность: {emb_vector.shape}")
                                continue
                            all_embeddings.append(emb_vector)
                            labels.append(product.name)
                            colors.append(color_map[product.name])
            except KeyError:
                continue
        
        # Проверка наличия данных
        if not all_embeddings or not prototypes:
            print("Нет данных для визуализации")
            return
            
        # Проверка совместимости размерностей
        try:
            combined = np.vstack([np.array(all_embeddings), np.array(prototypes)])
        except ValueError as e:
            print(f"Ошибка совместимости размерностей: {e}")
            print(f"Размер эмбеддингов: {np.array(all_embeddings).shape}")
            print(f"Размер прототипов: {np.array(prototypes).shape}")
            return
        
        # Снижение размерности
        if reduction_method == 'tsne':
            reducer = TSNE(n_components=2, random_state=42)
            embeddings_2d = reducer.fit_transform(combined)
        elif reduction_method == 'umap':
            reducer = umap.UMAP(random_state=42)
            embeddings_2d = reducer.fit_transform(combined)
        else:
            raise ValueError("Доступные методы: tsne или umap")
        
        # Разделение на эмбеддинги и прототипы
        proto_2d = embeddings_2d[len(all_embeddings):]
        emb_2d = embeddings_2d[:len(all_embeddings)]
        
        # Визуализация
        plt.figure(figsize=figsize)
        
        # Рисуем эмбеддинги
        for name in unique_names:
            mask = np.array(labels[:len(emb_2d)]) == name
            if mask.any():
                plt.scatter(
                    emb_2d[mask, 0],
                    emb_2d[mask, 1],
                    color=color_map[name],
                    label=name,
                    alpha=0.6,
                    s=40
                )
        
        # Рисуем прототипы
        for i, (x, y) in enumerate(proto_2d):
            plt.scatter(
                x,
                y,
                color=color_map[products[i].name],
                marker='*',
                s=400,
                edgecolor='black',
                linewidth=1,
                label=f'Proto: {products[i].name}'
            )
        
        plt.title(f"{reduction_method.upper()} проекция эмбеддингов (версия {version})")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()