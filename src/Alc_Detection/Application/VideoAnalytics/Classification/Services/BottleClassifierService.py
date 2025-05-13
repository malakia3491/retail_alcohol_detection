import cv2
from fastapi import UploadFile
import numpy as np
from torch import Tensor
import torch

import os
import torch
from PIL import Image

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
                           product_matrix: ProductMatrix
    ) -> ProductMatrix:
        product_matrix = product_matrix.copy()
        for id, shelf in product_matrix:
            crops = await self.extract_crops(image=img,
                                             boxes=shelf.boxes)
            embeddings = self.get_embeddings_from(crops)
            with torch.no_grad():
                labels = self._classifier(embeddings)
            products = self.convert_labels_to_products(labels)
            shelf.set_products(products)                   
        return product_matrix
    
    def convert_labels_to_products(self, labels: list[int]) -> list[Product]:
        return [self._cache.get(label) for label in labels]
    
    def load_classes(self, products: list[Product]):
        prototypes, labels, embs, lbs = self.__products_to_data(products, self._model.version)
        # self.visualize_embeddings(
        #     products=products,
        #     reduction_method="umap"
        # )
        if not None in prototypes:
            try:            
                self._classifier.fill(X=prototypes,
                                      Y=labels)
                # self._classifier.fit(embs, lbs)
                
                for product in products:
                    self._cache.put(product.label, product)
            except Exception as ex:
                raise ex
    
    def add_classes(self, products: list[Product]):
        try: 
            prototypes, labels, embs, lbs = self.__products_to_data(products, self._model.version)
            if len(prototypes) != 0 and len(labels) != 0 and len(prototypes) == len(labels):
                self._classifier.fine_fill(X=prototypes,
                                           Y=labels)
                for product in products:
                    self._cache.put(product.label, product)
        except Exception as ex:
            raise ex       
        
    async def preprocess(self, imgs) -> list[np.ndarray]:
        crops = []
        for img_file in imgs:                        
            img = await self._preprocessor.process(img_file, with_read=False) 
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
                transformed_crop = await self._preprocessor.resize(crop.cpu().numpy())
                crops.append(transformed_crop)         
            if not crops:
                return torch.empty(0)
            
            first_shape = crops[0].shape
            if not all(crop.shape == first_shape for crop in crops):
                raise ValueError("Все обрезки должны иметь одинаковый размер")
            
            batch = torch.stack(crops).to(self._device)
            return batch

    # async def extract_crops(
    #     self,
    #     image: torch.Tensor, # Входной тензор
    #     boxes: list, # Замените 'list' на list[ProductBox], если ProductBox определен
    #     save_pre_dir: str = "./pre_crops", # Изменил директории по умолчанию для наглядности
    #     save_post_dir: str = "./post_crops",
    # ) -> torch.Tensor:
    #     """
    #     Подготавливает тензор для классификационной модели и сохраняет изображения до/после препроцессинга.

    #     :param image: Исходный тензор изображения. Предполагается, что это (B, C, H, W) или (C, H, W),
    #                   значения могут быть нормализованы (например, [0,1] или [-1,1]),
    #                   а порядок каналов C - BGR, как указано в исходном docstring для "image".
    #     :param boxes: Список ProductBox с координатами.
    #     :param save_pre_dir: Директория для сохранения изображений до препроцессинга.
    #     :param save_post_dir: Директория для сохранения изображений после препроцессинга.
    #     :return: Тензор в формате [N, C, H, W] на нужном устройстве.
    #     """
    #     # Важно: cv2 работает с NumPy массивами и ожидает BGR порядок каналов по умолчанию.
    #     # Изображения для сохранения должны быть в формате (H, W, C) и dtype=np.uint8 со значениями [0, 255].

    #     # 1. Подготовка исходного изображения
    #     #    Конвертируем тензор в NumPy массив (H, W, C) на CPU.
    #     #    Исходный docstring говорит "BGR image (H, W, 3)" для параметра image,
    #     #    но `.squeeze(0).permute(1, 2, 0)` намекает, что image - это (1, C, H, W) или (C, H, W).
    #     #    Будем считать, что после permute() мы получаем (H, W, C) с BGR каналами.
    #     if image.ndim == 4 and image.shape[0] == 1:
    #         img_for_cropping_HWC = image.squeeze(0).permute(1, 2, 0)  # (1, C, H, W) -> (C, H, W) -> (H, W, C)
    #     elif image.ndim == 3:
    #         img_for_cropping_HWC = image.permute(1, 2, 0)  # (C, H, W) -> (H, W, C)
    #     else:
    #         # Если формат уже (H, W, C) и это тензор, возможно, ничего делать не надо или permute другой
    #         # Для безопасности, если формат неожиданный, можно вызвать ошибку или адаптировать.
    #         # Пока предполагаем, что это один из вышеуказанных.
    #         # Если он уже (H,W,C) и тензор, просто .cpu().numpy()
    #         if image.shape[2] == 3: # Наиболее вероятно (H,W,C)
    #              img_for_cropping_HWC = image
    #         else:
    #             raise ValueError(f"Unexpected image tensor shape: {image.shape}. Expected (B,C,H,W) or (C,H,W).")


    #     img_for_cropping_HWC_np = img_for_cropping_HWC.cpu().numpy()
    #     # Теперь img_for_cropping_HWC_np это NumPy массив (H, W, C), BGR,
    #     # но значения могут быть float и нормализованы (например, [0,1] или [-1,1]).

    #     crops_for_model = []

    #     for idx, box in enumerate(boxes):
    #         x1, y1 = int(box.p_min.x), int(box.p_min.y)
    #         x2, y2 = int(box.p_max.x), int(box.p_max.y)
            
    #         h_img, w_img, _ = img_for_cropping_HWC_np.shape
    #         x1, y1 = max(0, x1), max(0, y1)
    #         x2, y2 = min(w_img, x2), min(h_img, y2)
    #         if x1 >= x2 or y1 >= y2: # Если после клиппинга бокс стал невалидным
    #             print(f"Warning: Skipping box {idx} after clipping to image bounds: ({x1},{y1})-({x2},{y2})")
    #             continue

    #         # 2. Вырезаем кроп
    #         # crop_np_raw все еще может быть float и нормализованным
    #         crop_np_raw = img_for_cropping_HWC_np[y1:y2, x1:x2, :].copy() # .copy() чтобы избежать проблем со слайсами

    #         if crop_np_raw.size == 0: # Пропускаем пустые кропы
    #             print(f"Warning: Skipping empty crop {idx} from box: ({x1},{y1})-({x2},{y2})")
    #             continue

    #         # 3. Подготовка кропа для сохранения "до препроцессинга" (pre)
    #         #    Нужно конвертировать в uint8 [0, 255], BGR.
    #         #    Предполагаем, что crop_np_raw уже BGR по порядку каналов.
            
    #         # Создаем версию для сохранения (uint8, [0,255])
    #         # Эта версия также будет передана в препроцессор, если он ожидает uint8
    #         crop_to_save_or_process_uint8: np.ndarray
    #         if crop_np_raw.dtype != np.uint8:
    #             min_val, max_val = crop_np_raw.min(), crop_np_raw.max()
    #             if 0.0 <= min_val and max_val <= 1.0 + 1e-5:  # Типичная нормализация [0, 1]
    #                 crop_to_save_or_process_uint8 = (crop_np_raw * 255.0).astype(np.uint8)
    #             elif -1.0 - 1e-5 <= min_val and max_val <= 1.0 + 1e-5: # Типичная нормализация [-1, 1]
    #                 # Преобразуем [-1,1] в [0,1], затем в [0,255]
    #                 normalized_01 = (crop_np_raw + 1.0) / 2.0
    #                 crop_to_save_or_process_uint8 = (normalized_01 * 255.0).astype(np.uint8)
    #             else: # Диапазон float, но не [0,1] или [-1,1] (например, уже [0,255] но float)
    #                 crop_to_save_or_process_uint8 = np.clip(crop_np_raw, 0, 255).astype(np.uint8)
    #         else: # Уже uint8
    #             crop_to_save_or_process_uint8 = crop_np_raw.astype(np.uint8) # Убедимся, что это uint8

    #         # Сохраняем до препроцессинга
    #         if save_pre_dir:
    #             # crop_to_save_or_process_uint8 уже BGR, uint8, [0, 255]
    #             cv2.imwrite(os.path.join(save_pre_dir, f"pre_{idx}.jpg"), crop_to_save_or_process_uint8)

    #         # 4. Применяем препроцессинг
    #         #    Предполагаем, что self._preprocessor.resize ожидает NumPy массив (H,W,C), uint8, BGR
    #         #    и возвращает тензор (C,H,W) для модели (вероятно, RGB и нормализованный).
    #         transformed_crop_tensor = await self._preprocessor.resize(crop_to_save_or_process_uint8)
            
    #         # 5. Подготовка и сохранение кропа "после препроцессинга" (post)
    #         if save_post_dir:
                
    #             post_np: np.ndarray
    #             if isinstance(transformed_crop_tensor, torch.Tensor):
    #                 # Конвертируем тензор (C, H, W) в NumPy (H, W, C)
    #                 post_np = transformed_crop_tensor.permute(1, 2, 0).cpu().numpy()
    #             else: # Если препроцессор вернул NumPy массив (H,W,C)
    #                 post_np = transformed_crop_tensor

    #             # Конвертируем в uint8 [0, 255] для сохранения
    #             # Эта логика из оригинального кода кажется корректной
    #             if post_np.dtype != np.uint8:
    #                 min_val_post, max_val_post = post_np.min(), post_np.max()
    #                 if 0.0 <= min_val_post and max_val_post <= 1.0 + 1e-5: # Нормализация [0, 1]
    #                     post_np = (post_np * 255.0)
    #                 elif -1.0 - 1e-5 <= min_val_post and max_val_post <= 1.0 + 1e-5: # Нормализация [-1, 1]
    #                     normalized_01_post = (post_np + 1.0) / 2.0
    #                     post_np = (normalized_01_post * 255.0)
    #                 # Если уже float в диапазоне [0,255], то clip ниже это обработает
                
    #             post_np_save = np.clip(post_np, 0, 255).astype(np.uint8)

    #             # # Преобразуем RGB -> BGR, если необходимо (cv2.imwrite ожидает BGR)
    #             # # Предполагаем, что препроцессор мог изменить порядок каналов на RGB (стандарт для моделей)
    #             # if post_np_save.shape[2] == 3: # Только для цветных изображений
    #             #     post_np_save = post_np_save[..., ::-1]  # RGB -> BGR

    #             cv2.imwrite(os.path.join(save_post_dir, f"post_{idx}.jpg"), post_np_save)

    #         crops_for_model.append(transformed_crop_tensor) # Собираем тензоры для батча

    #     if not crops_for_model:
    #         return torch.empty(0, device=self._device) # Возвращаем пустой тензор, если нет кропов

    #     # Проверка, что все кропы имеют одинаковый размер (если это требование)
    #     # Эта проверка должна быть после препроцессинга, так как он стандартизирует размер
    #     first_shape = crops_for_model[0].shape
    #     if any(crop.shape != first_shape for crop in crops_for_model):
    #         # Если размеры могут отличаться, нужно будет использовать кастомный collate_fn для DataLoader
    #         # или паддить/ресайзить дополнительно здесь.
    #         # Для простоты пока оставим ValueError.
    #         # Можно добавить логирование размеров для отладки:
    #         # for i, crop_item in enumerate(crops_for_model):
    #         #    print(f"Crop {i} shape: {crop_item.shape}")
    #         raise ValueError(f"Все обработанные кропы должны иметь одинаковый размер. Первый: {first_shape}, найдены другие.")

    #     return torch.stack(crops_for_model).to(self._device)


    def __products_to_data(self,
                           products: list[Product],
                           version: str
    ) -> tuple[np.ndarray[np.ndarray], np.ndarray]:
        labels = []
        prototypes = []
        embeddings = []
        embeddings_labels = []
        for product in products:
            if product.is_classificated:
                emb = product.embeddings(version)
                embeddings.extend(emb)
                l = []
                for e in emb:
                    l.append(product.label)
                embeddings_labels.extend(l)   
                prototypes.append(product.get_prototype(version))        
                labels.append(product.label)
            else: continue        
        return np.array(prototypes), np.array(labels), np.array(embeddings), np.array(embeddings_labels)

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
        
        expected_dim = 256  # Ожидаемая размерность эмбеддингов
        
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
                            all_embeddings.append(emb.vector)
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
        
        print("ВСЕГО ВЕКТОРОВ В ФУНКЦИИ", len(all_embeddings))
        print("ВСЕГО МЕТОК В ФУНКЦИИ", len(labels))
        print("ВСЕГО ВЕКТОРОВ В ФУНКЦИИ", len(prototypes))
        
        
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