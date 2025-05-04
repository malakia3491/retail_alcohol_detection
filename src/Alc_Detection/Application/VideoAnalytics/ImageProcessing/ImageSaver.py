import cv2
import os
import torch
import uuid
import numpy as np

from pathlib import Path
from PIL import Image

from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Domain.Store.Product import Product

class ImageSaver:
    def __init__(self,
                 product_crop_save_dir: str,
                 realogram_save_dir: str,
                 planogram_save_dir: str
    ):
        self._path_dict: dict[str, str] = {
            Product.__name__:  product_crop_save_dir,
            Realogram.__name__: realogram_save_dir,
            Planogram.__name__: planogram_save_dir,
        } 
        
    def get_path(self, obj_type):
        try:
            return self._path_dict[obj_type.__name__]
        except Exception as ex:
            raise ex
    
    def save_(self, image, save_dir: str, obj_type: type, file_ext: str = ".jpg") -> str:
            """
            Сохраняет изображение (тензор, PIL.Image, numpy.ndarray) в указанную директорию.
            
            :param image: Изображение для сохранения (torch.Tensor, PIL.Image, np.ndarray)
            :param save_dir: Поддиректория внутри базового пути для типа объекта
            :param obj_type: Тип объекта (Product, Realogram, Planogram)
            :param file_ext: Расширение файла (по умолчанию .jpg)
            :return: Полный путь к сохраненному файлу
            """
            try:
                # Проверка типа объекта
                obj_type_name = obj_type.__name__
                if obj_type_name not in self._path_dict:
                    raise ValueError(f"Тип объекта {obj_type_name} не поддерживается")

                # Получение базового пути и создание директории
                base_path = self._path_dict[obj_type_name]
                full_save_dir = os.path.join(base_path, save_dir)
                Path(full_save_dir).mkdir(parents=True, exist_ok=True)
                
                # Проверка прав на запись
                if not os.access(full_save_dir, os.W_OK):
                    raise PermissionError(f"Нет доступа к директории: {full_save_dir}")

                # Валидация изображения
                if image is None:
                    raise ValueError("Изображение не может быть None")
                    
                # Определение расширения файла
                file_ext = file_ext.lower()
                if file_ext not in {".jpg", ".jpeg", ".png"}:
                    file_ext = ".jpg"

                # Генерация имени файла
                file_name = f"{uuid.uuid4()}{file_ext}"
                save_path = os.path.join(full_save_dir, file_name)

                # Сохранение в зависимости от типа
                if isinstance(image, torch.Tensor):
                    self.save_tensor_as_image(image, save_path)
                elif isinstance(image, Image.Image):
                    image.save(save_path)
                elif isinstance(image, np.ndarray):
                    cv2.imwrite(save_path, image)
                else:
                    raise TypeError(f"Неподдерживаемый тип изображения: {type(image)}")

                # Проверка успешности сохранения
                if not os.path.exists(save_path):
                    raise FileNotFoundError(f"Файл не создан: {save_path}")

                return save_path

            except Exception as ex:
                error_msg = (
                    f"Ошибка сохранения: {ex}\n"
                    f"Путь: {save_path}\n"
                    f"Тип объекта: {obj_type_name}\n"
                    f"Тип изображения: {type(image)}"
                )
                raise type(ex)(error_msg) from ex
    
    def save(self, image_file, image, save_dir, obj_type):
        try:
            obj_type_name = obj_type.__name__
            if obj_type_name not in self._path_dict:
                raise ValueError(f"Тип объекта {obj_type_name} не найден в path_dict")

            base_path = self._path_dict[obj_type_name]
            full_save_dir = os.path.join(base_path, save_dir)
            
            Path(full_save_dir).mkdir(parents=True, exist_ok=True)
            if not os.access(full_save_dir, os.W_OK):
                raise PermissionError(f"Нет прав на запись в директорию: {full_save_dir}")

            if image is None or image.size == 0:
                raise ValueError("Изображение пустое или некорректное")
                
            original_filename = getattr(image_file, 'filename', 'unknown')
            file_ext = os.path.splitext(original_filename)[1].lower()
            if not file_ext or file_ext not in {'.jpg', '.jpeg', '.png'}:
                file_ext = '.jpg'

            file_name = f"{uuid.uuid4()}{file_ext}"
            save_path = os.path.join(full_save_dir, file_name)

            self.save_tensor_as_image(tensor=image,
                                      save_path=save_path)

            if not os.path.exists(save_path):
                raise FileNotFoundError(f"Файл не был создан: {save_path}")

            return save_path

        except Exception as ex:
            error_msg = (f"Ошибка сохранения изображения: {str(ex)}\n"
                        f"Путь: {save_path}\n"
                        f"Тип объекта: {obj_type_name}\n"
                        f"Размер изображения: {image.shape if image is not None else 'N/A'}")
            raise type(ex)(error_msg) from ex
                
    def save_tensor_as_image(
        self,
        tensor: torch.Tensor, 
        save_path: str,
        denormalize: bool = True,
        mean: list = [0.5, 0.5, 0.5],
        std: list = [0.5, 0.5, 0.5]
    ) -> None:
        """
        Сохраняет тензор в формате [B, C, H, W] как изображение
        :param tensor: Входной тензор shape [1, 3, H, W]
        :param save_path: Путь для сохранения (включая расширение)
        :param denormalize: Применять обратную нормализацию
        :param mean: Средние значения для денормализации
        :param std: Стандартные отклонения для денормализации
        """
        try:
            if tensor.dim() == 4:
                if tensor.size(0) != 1:
                    raise ValueError("Тензор должен быть в формате [1, C, H, W]")
                img_tensor = tensor.squeeze(0).cpu().detach()
            else:
                img_tensor = tensor.cpu().detach()
            

            if denormalize:
                mean = torch.tensor(mean).view(3, 1, 1)
                std = torch.tensor(std).view(3, 1, 1)
                img_tensor = img_tensor * std + mean  
                img_tensor = torch.clamp(img_tensor, 0, 1) 

            numpy_image = img_tensor.permute(1, 2, 0).numpy() 
            numpy_image = (numpy_image * 255).astype(np.uint8)

            # if numpy_image.shape[2] == 3:
            #     numpy_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            if not cv2.imwrite(save_path, numpy_image):
                raise RuntimeError(f"Ошибка сохранения: {save_path}")

        except Exception as e:
            raise RuntimeError(f"Ошибка обработки тензора: {str(e)}") from e