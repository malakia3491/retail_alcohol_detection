from fastapi import UploadFile
import numpy as np
import cv2
from typing import Tuple, List
import torch
from torchvision import transforms
from torch import stack
from PIL import Image
import io

from Alc_Detection.Application.VideoAnalytics.Exceptions.Exceptions import NotCorrectImageFile

class ImagePreprocessor:
    def __init__(self,
                 device: str = "cpu",
                 output_size: Tuple[int, int] = (128, 128),
                 mean: List[float] = [0.5, 0.5, 0.5],
                 std: List[float] = [0.5, 0.5, 0.5]
                 ):
        self.target_size = output_size
        self.device = device
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(output_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std)    
        ])
        self.allowed_mime_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        
    def build(self,
              device: str = "cpu",
              output_size: Tuple[int, int] = (640, 640),
              mean: List[float] = [0.5, 0.5, 0.5],
              std: List[float] = [0.5, 0.5, 0.5]
              ) -> 'ImagePreprocessor':
        self.device = device
        self.target_size = output_size
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std)
        ])
        return self
    
    def _format_bytes_to_image(self, bytes: bytes):
        nparr = np.frombuffer(bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)    
        return img
    
    def validate(self, file: UploadFile, contents: bytes):
        ex = NotCorrectImageFile(file_name=file.filename,
                                 mime_type=file.content_type,
                                 verify=False)
        if file.content_type not in self.allowed_mime_types:
            raise ex 
        try:
            with Image.open(io.BytesIO(contents)) as img:
                img.verify()
        except Exception:
            raise ex
        
    async def load(self, image_file: UploadFile):
        contents = await image_file.read()
        self.validate(file=image_file, contents=contents)             
        processed_image = self._format_bytes_to_image(contents)
        return processed_image
        
    async def resize(self, img, output_size=(128, 64)):
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(output_size),
            transforms.ToTensor(),
        ])
        return transform(img)
    
    async def process(self, image_file: UploadFile, with_read=True):
        """
        Преобразует список изображений в тензор и перемещает его на указанное устройство.
        
        :param images: Список изображений в формате массива или тензора.
        :return: Тензор с добавленной размерностью батча и перенесённый на device.
        """
        if with_read:
            contents = await image_file.read()
            self.validate(file=image_file, contents=contents)             
            processed_image = self._format_bytes_to_image(contents)
            transformed_image = self.transform(processed_image)
            transformed_image = transformed_image.unsqueeze(0).to(self.device)
        else:
            processed_image = image_file
            transformed_image = self.transform(processed_image)
            transformed_image = transformed_image.to(self.device)

        return transformed_image
    
    