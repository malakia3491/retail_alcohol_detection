import abc

from fastapi import UploadFile

class ShelfService(abc.ABC):
    @abc.abstractmethod
    def handle_shelf_image(self, image_file: UploadFile, shelving_id: str, store_id: str) -> None:
        pass
    
    @abc.abstractmethod
    async def define_boxes_for_planogram_products(self, image_file: UploadFile, shelving_id: str, store_id: str) -> None:
        pass