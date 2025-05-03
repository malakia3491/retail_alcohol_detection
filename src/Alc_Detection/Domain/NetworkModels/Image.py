import os
import re
import cv2
import imghdr
import PIL.Image
import numpy as np
from pathlib import Path

from Alc_Detection.Domain.Exceptions.Exceptions import ImageError
from Alc_Detection.Domain.NetworkModels.EmbeddingModel import EmbeddingNetwork
from Alc_Detection.Domain.NetworkModels.Embedding import Embedding

class Image:
    def __init__(self,
                 path: str,
                 embeddings: list[Embedding]
    ):
        if self.validate_image_file(file_path=path):
            self._path = path
        else: raise ImageError(path)
        self._embeddings = embeddings
        
    @property
    def model(self) -> EmbeddingNetwork:
        return self.embeddings[0].model
        
    @property
    def name(self) -> str:
        match = re.search(r'([a-f0-9\-]{36})\\[a-f0-9\-]{36}\.jpg$', self._path, re.IGNORECASE)
        if match:
            return match.group(1)
        raise ValueError("UUID not found in the image path")
    
    @property
    def path(self) -> str:
        return self._path   
      
    @property
    def embeddings(self) -> list[Embedding]:
        return self._embeddings
    
    def load(self) -> np.ndarray:
        try:
            image_cv = cv2.imread(self.path)
        except Exception as ex:
            raise ImageError(self._path)

        if image_cv is None:
            raise FileNotFoundError(f"Изображение по пути {self.path} не найдено!")

    def copy(self) -> 'Image':
        return Image(path=self._path,
                     embeddings=self._embeddings)
    
    def validate_image_file(self, file_path: str | Path, allowed_formats: list = ['jpg', 'jpeg', 'png']) -> bool:
        """
        Проверяет файл изображения без загрузки в память
        :param file_path: Путь к файлу
        :param allowed_formats: Допустимые форматы (['jpeg', 'png', etc])
        :return: True если файл корректен
        """
        if not os.path.exists(file_path):
            return False
        if not os.path.isfile(file_path):
            return False
        
        with open(file_path, 'rb') as f:
            header = f.read(16)
        
        detected_format = imghdr.what(None, header)
        
        if not detected_format:
            return False
        if allowed_formats and detected_format not in allowed_formats:
            return False

        try:
            with PIL.Image.open(file_path) as img:
                img.verify()
        except Exception as e:
            return False
        return True