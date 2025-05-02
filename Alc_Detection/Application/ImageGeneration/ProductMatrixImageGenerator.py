import os
from typing import Type
from Alc_Detection.Domain.Store.Product import Product
from PIL import Image

from Alc_Detection.Domain.Shelf.ProductMatrix.ProductMatrix import ProductMatrix
from Alc_Detection.Application.VideoAnalytics.ImageProcessing.ImageSaver import ImageSaver


class ProductMatrixImageGenerator:
    def __init__(self,
                 image_saver: ImageSaver
    ):
        self._image_save = image_saver
    def generate(self,
                 id_name: str,
                 product_matrix: ProductMatrix,
                 obj_type: Type,
                 cell_size: tuple[int, int]=(64, 64)
    ) -> str:
        """
        Собирает изображение планограммы из изображений товаров, размещенных в матрице.
        
        :param product_matrix: Экземпляр ProductMatrix с информацией о расположении товаров.
        :param image_saver: Экземпляр ImageSaver для получения путей к изображениям.
        :param cell_size: Размер (ширина, высота) каждой ячейки на планограмме.
        :return: Изображение планограммы в формате PIL.Image.
        """
        # Проверяем наличие полок в матрице
        shelves = product_matrix._shelves.values()
        if not shelves:
            return Image.new('RGB', (0, 0))  # Пустое изображение
        
        # Определяем размеры планограммы
        max_boxes = max(len(shelf.boxes) for shelf in shelves)
        rows = len(shelves)
        cell_width, cell_height = cell_size
        planogram_width = max_boxes * cell_width
        planogram_height = rows * cell_height
        
        # Создаем пустое изображение
        planogram_img = Image.new('RGB', (planogram_width, planogram_height), 'white')
        
        # Перебираем все полки и боксы
        for shelf_idx, shelf in product_matrix._shelves.items():
            for box_idx, box in enumerate(shelf.boxes):
                if box.is_empty:
                    continue  # Пропускаем пустые боксы
                
                product = box.product
                if not product or not product.id:
                    continue  # Нет информации о товаре
                
                # Получаем путь к папке с изображениями товара
                product_crop_dir = self.image_saver._path_dict.get(Product.__name__)
                if not product_crop_dir:
                    continue
                product_dir = os.path.join(product_crop_dir, str(product.id))
                
                # Ищем первое изображение товара
                try:
                    image_files = sorted(os.listdir(product_dir))
                    if not image_files:
                        continue
                    first_image = image_files[0]
                    image_path = os.path.join(product_dir, first_image)
                except FileNotFoundError:
                    continue
                
                # Загружаем и обрабатываем изображение
                try:
                    img = Image.open(image_path)
                except Exception:
                    continue
                
                # Масштабируем изображение с сохранением пропорций
                img.thumbnail(cell_size)
                # Создаем фон ячейки и вставляем изображение по центру
                cell_img = Image.new('RGB', cell_size, 'white')
                img_w, img_h = img.size
                offset = ((cell_width - img_w) // 2, (cell_height - img_h) // 2)
                cell_img.paste(img, offset)
                
                # Позиция на планограмме
                x = box_idx * cell_width
                y = shelf_idx * cell_height
                # Вставляем ячейку в планограмму
                planogram_img.paste(cell_img, (x, y))
        
        path = self._image_save.save_(
            image=planogram_img,
            save_dir=id_name,
            obj_type=obj_type
        )
        
        return path