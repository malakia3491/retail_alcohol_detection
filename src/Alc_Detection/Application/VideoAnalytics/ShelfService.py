from datetime import datetime
import traceback
from Alc_Detection.Application.IncidentManagement.Services.IncidentManager import IncidentManager
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Persistance.Repositories.StoreRepository import StoreRepository
from PIL import Image, ImageDraw
import cv2
import numpy as np
from collections import defaultdict
from fastapi import HTTPException, UploadFile, status
from sklearn.cluster import AgglomerativeClustering
from ultralytics.engine.results import Results 

from Alc_Detection.Application.Requests.Models import CalibrationBoxesResponse
from Alc_Detection.Application.Requests.Requests import AddCalibrationBoxesRequest
from Alc_Detection.Application.StoreInformation.Services.StoreServiceFacade import StoreService
from Alc_Detection.Application.VideoAnalytics.ImageProcessing.ImageSaver import ImageSaver
from Alc_Detection.Domain.Entities import *
from Alc_Detection.Application.VideoAnalytics.Exceptions.Exceptions import NotCorrectImageFile
from Alc_Detection.Application.VideoAnalytics.ImageProcessing.ImagePreprocessor import ImagePreprocessor
from Alc_Detection.Application.VideoAnalytics.Detection.Services.BottleModelDetectionService import BottleModelDetectionService
from Alc_Detection.Application.VideoAnalytics.Detection.Services.PersonDetectionService import PersonDetectionService
from Alc_Detection.Application.VideoAnalytics.Classification.Services.BottleClassifierService import BottleClassifierService
from Alc_Detection.Application.Requests.Models import CalibrationBox as CalibrationBoxModel 
from Alc_Detection.Domain.NetworkModels.Embedding import Embedding
from Alc_Detection.Domain.NetworkModels.EmbeddingModel import EmbeddingNetwork
from Alc_Detection.Domain.NetworkModels.Image import Image
from Alc_Detection.Domain.Shelf.ProductMatrix.CalibrationBox import CalibrationBox
from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Persistance.Repositories.EmbeddingModelRepository import EmbeddingModelRepository
from Alc_Detection.Persistance.Repositories.ProductRepository import ProductRepository

class ShelfService:
    def __init__(self,
                 preprocessor: ImagePreprocessor,
                 person_detector: PersonDetectionService,
                 bottle_detector: BottleModelDetectionService,
                 bottle_classifier: BottleClassifierService,
                 store_service: StoreService,
                 product_repository: ProductRepository,
                 embedding_network_repository: EmbeddingModelRepository,
                 store_repository: StoreRepository,
                 image_saver: ImageSaver,
                 incident_management_service: IncidentManager):
        self.preprocessor = preprocessor
        self.person_detector = person_detector
        self.bottle_detector = bottle_detector
        self.bottle_classifier = bottle_classifier
        self.incident_management_service = incident_management_service
        self._product_repository = product_repository
        self._embedding_network_repository = embedding_network_repository
        self._image_saver = image_saver
        self._store_repository = store_repository
        self.store_service = store_service
    
    async def on_start(self) -> None:
        products = await self._product_repository.get_all()
        self.bottle_classifier.on_start(products=products)
        model_id = self._embedding_network_repository.index(self.bottle_classifier.model)
        self.bottle_classifier.model.id = model_id 
        
    async def add_product_images(self,
                                 product_id: str,
                                 image_files: list[UploadFile]
    ) -> str:
        try:          
            product = await self._product_repository.get(product_id)
            images = await self.bottle_classifier.preprocess(image_files)
            embeddings = self.bottle_classifier.get_embeddings_from(images).cpu().numpy()                 
            product_images = []
            for img, emb, file in zip(images, embeddings, image_files):
                path = self._image_saver.save(image_file=file,
                                              image=img,
                                              save_dir=str(product_id),
                                              obj_type=Product)
                embedding = Embedding(cords=emb,
                                      model=self.bottle_classifier.model)
                product_images.append(Image(path=path,
                                            embeddings=[embedding]))
            product.add_images(*product_images)
            added_records_count = await self._product_repository.add_imgs(product, *product_images)
            self.bottle_classifier.add_classes([product])
            return f"Succsessfully. Added {added_records_count} records."
        except Exception as ex:
            raise ex
    
    async def calibrate_planogram(self,
                                  request: AddCalibrationBoxesRequest
    ) -> str:
        positions = self._get_calibration_box_positions(request.calibration_boxes)
        
        calibration_boxes = [CalibrationBox(xyxy=box.xyxy,
                                            matrix_cords=position,
                                            conf=box.conf)
                             for box, position in zip(request.calibration_boxes, positions)]
        
        message = await self.store_service.calibrate_store_planogram(
            person_id=request.person_id,
            store_id=request.store_id,
            order_id=request.order_id,
            shelving_id=request.shelving_id,
            calibration_boxes=calibration_boxes
        )
        return message         
    
    async def get_calibration_boxes(self, 
                                    image_file: UploadFile
    ) -> CalibrationBoxesResponse:
        try:            
            img, result = await self._get_detection_result(image_file)
            calibration_boxes: list[CalibrationBox] = self.convert_yolo_to_calibration_boxes(result)        
            return CalibrationBoxesResponse(calibration_boxes=calibration_boxes)
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ex.__str__()
            )
        
    async def handle_shelf_image(self, image_file: UploadFile, shelving_id: str, store_id: str) -> None:
        store = await self._store_repository.get(store_id)
        planogram = await self.store_service.get_calibrated_planogram(store_id=store.id,
                                                                      shelving_id=shelving_id)       
        img, product_matrix = await self._get_product_matrix_by_shelf_image(image_file)       
        if product_matrix is not None:
            product_matrix = await self.bottle_classifier.classificate(img, product_matrix)
            product_matrix = self._get_realogram(product_matrix,
                                                 planogram.product_matrix,
                                                 img.shape)
            
            path = self._image_saver.save(image_file=image_file,
                                          image=img,
                                          save_dir=str(datetime.now().date()),
                                          obj_type=Realogram)
            realogram = Realogram(
                planogram=planogram,
                product_matrix=product_matrix,
                create_date=datetime.now(),
                img_src=path
            )
            
            store.add_realogram(realogram)
            result_count = await self._store_repository.add_realogram(store, realogram)
            await self.incident_management_service.handle_realogram(
                                                    store=store,
                                                    realogram=realogram
            )
            return f"Successfully. {result_count} shelving image is handled"
        return "Persons have been found on image. It does not handled"                          
    
    async def _get_product_matrix_by_shelf_image(self, image_file: UploadFile):
        try:
            img, result = await self._get_detection_result(image_file)    
            product_matrix = self._get_product_matrix_by_model_result(result.boxes)
               
            return img, product_matrix
        except NotCorrectImageFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image content"
            ) 
      
    async def _get_detection_result(self, image_file: UploadFile) -> Results:
        try:    
            pil_img = await self.preprocessor.load(image_file)
            processed_img = await self.preprocessor.process(pil_img, with_read=False)
            person_detection_result = self.person_detector.detect_persons_on(pil_img) 
            if len(person_detection_result.boxes) == 0:
                bottles_detection_result = self.bottle_detector.detect_bottles_on(processed_img=pil_img)
                return processed_img, bottles_detection_result
            return None
        except NotCorrectImageFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image content"
            )                    
        
    def _get_realogram(self,
                       product_matrix: ProductMatrix,
                       planogram: ProductMatrix,
                       img_shape: tuple[int, int]
    ) -> ProductMatrix:
        realogram = product_matrix.copy()
        if product_matrix.is_empty:
            realogram = planogram.copy()
            realogram.is_empty = True
            return realogram
        self._find_empty_shelfs(product_matrix=realogram,
                                planogram=planogram,
                                img_shape=img_shape)
        self._find_empty_boxes(product_matrix=realogram,
                               planogram=planogram,
                               img_shape=img_shape)
        return realogram
     
    def _get_product_matrix_by_model_result(
        self, boxes: np.ndarray
    ) -> tuple[str, tuple[int, int], ProductMatrix]:
        """
        Преобразует результат модели (список боксов) в ProductMatrix,
        где полки упорядочены сверху вниз.
        """
        if not boxes:
            return ProductMatrix(shelves=None, is_empty=True)
        product_boxes = [
            ProductBox().load_coordinates(xyxy=b.xyxy[0].cpu().numpy(), conf=b.conf)
            for b in boxes
        ]
        centers = np.array([p.center.y for p in product_boxes]).reshape(-1, 1)
        thresh = self._compute_distance_threshold(centers.flatten())        
        clustering = AgglomerativeClustering(
            distance_threshold=thresh,
            n_clusters=None
        ).fit(centers)
        
        groups: dict[int, list[ProductBox]] = {}
        for lbl, pb in zip(clustering.labels_, product_boxes):
            groups.setdefault(lbl, []).append(pb)

        cluster_avg_y = {
            lbl: np.mean([box.center.y for box in boxes])
            for lbl, boxes in groups.items()
        }
        sorted_clusters = sorted(
            groups.keys(),
            key=lambda x: cluster_avg_y[x]
        )

        shelves: dict[int, Shelf] = {
            shelf_idx: Shelf(groups[lbl])
            for shelf_idx, lbl in enumerate(sorted_clusters)
        }
        matrix = ProductMatrix(shelves=shelves).define_positions()     
        return matrix
    
    def _compute_distance_threshold(self, y_coords: np.ndarray[int]) -> float:
        """
        Вычисляет порог (distance_threshold) на основе координат Y центров товаров.
        
        Параметры:
        - y_coords: список или массив координат Y центров товаров.
        - plot: если True, то отображает график распределения разностей для визуальной оценки.
        
        Возвращает:
        - threshold: вычисленный порог расстояния между товарами.
        """
        y_sorted = np.sort(np.array(y_coords))
        diffs = np.diff(y_sorted)
        elbow_idx = np.argmax(diffs)
        threshold = (y_sorted[elbow_idx] + y_sorted[elbow_idx + 1]) / 4.0
        
        return threshold
    
    def _find_empty_shelfs(
        self,
        product_matrix: ProductMatrix,
        planogram: ProductMatrix,
        img_shape: tuple[int, int],
        margin: int = 10,
    ) -> ProductMatrix:
        """
        Вставляет пустые полки в gaps между обнаруженными полками
        """
        result_matrix = product_matrix.copy()
        total_plan_shelves = planogram.len_shelves
        detected = product_matrix.len_shelves

        if detected > 0:
            heights = [shelf.height for _, shelf in product_matrix]
            mean_height = np.mean(heights)

            if detected < total_plan_shelves:
                for idx in range(product_matrix.len_shelves):
                    shelf = product_matrix[idx]
                    top_y = shelf.height_point.x

                    if idx == 0:
                        prev_idx = -1
                        prev_bottom = 0
                    else:
                        prev_shelf = product_matrix[idx - 1]
                        prev_bottom = prev_shelf.height_point.y

                    gap = top_y - prev_bottom
                    if gap > mean_height:
                        n_new = int((gap - margin) // shelf.height)
                        
                        new_shelves: dict[int, Shelf] = {
                            j: Shelf(
                                [ProductBox(is_empty=True) for _ in range(len(planogram[idx]))],
                                is_empty=True
                            ) for j in range(n_new)
                        }
                        result_matrix.insert_shelves(new_shelves, (prev_idx, idx))
                        detected += n_new
                    if detected == total_plan_shelves:
                        break

            if detected < total_plan_shelves:
                last_idx = product_matrix.len_shelves - 1
                last_shelf = product_matrix[last_idx]
                bottom_y = last_shelf.height_point.y
                image_bottom = img_shape[1]
                gap = image_bottom - bottom_y
                if gap > mean_height:
                    n_new = int((gap - margin) // last_shelf.height)
                    new_shelves = {
                        j: Shelf(
                            [ProductBox(is_empty=True) for _ in range(len(planogram[last_idx]))],
                            is_empty=True
                        ) for j in range(n_new)
                    }
                    result_matrix.insert_shelves(new_shelves, (last_idx, product_matrix.len_shelves))
                    detected += n_new

        return result_matrix
                                   
    def _find_empty_boxes(
        self,
        product_matrix: ProductMatrix,
        planogram: ProductMatrix,
        img_shape: tuple[int, int]
    ) -> ProductMatrix:
        """
        Вставляет пустые боксы между найденными элементами и заменяет полностью пустые полки
        """
        result_matrix = product_matrix.copy()
        for idx in range(product_matrix.len_shelves):
            shelf = result_matrix[idx]
            plan_shelf = planogram[idx]

            if not shelf.is_empty:
                boxes = [b.copy() for b in shelf.boxes]
                for i, curr in enumerate(boxes):
                    prev_x = 0 if i == 0 else boxes[i-1].width_point.y
                    curr_x = curr.width_point.x
                    to_insert = plan_shelf.get_boxes_between(prev_x, curr_x)
                    if to_insert:
                        for b in to_insert:
                            b.is_empty = True
                        shelf.insert_boxes(to_insert, i)
                        
                last_x = boxes[-1].width_point.y
                end_x = img_shape[0]
                to_insert = plan_shelf.get_boxes_between(last_x, end_x)
                if to_insert:
                    for b in to_insert:
                        b.is_empty = True
                    shelf.insert_boxes(to_insert, len(shelf))
            else:
                empty_boxes = []
                for b in plan_shelf.boxes:
                    copy_b = b.copy()
                    copy_b.is_empty = True
                    empty_boxes.append(copy_b)
                shelf.set_boxes(empty_boxes)
        return result_matrix
     
    def convert_yolo_to_calibration_boxes(self,
                                          result: Results
    ) -> list[CalibrationBox]:
        """
        Конвертирует результаты YOLOv8 в список CalibrationBox.
        
        Параметры:
        - yolo_results: Результат работы модели YOLO (объект с полем boxes)
        
        Возвращает:
        - Список CalibrationBox с координатами и уверенностью
        """
        boxes = result.boxes
        calibration_boxes = []
        
        # Если нет обнаруженных боксов
        if not boxes:
            return calibration_boxes
        
        # Извлекаем данные из тензоров
        for box in boxes:
            # Конвертируем координаты из тензора в список int
            xyxy = box.xyxy[0].cpu().numpy().astype(np.int32).tolist()
            
            # Извлекаем уверенность
            conf = box.conf[0].cpu().item()
            
            calibration_boxes.append(
                CalibrationBoxModel(xyxy=xyxy, conf=conf)
            )
        
        return calibration_boxes 
       
    def _get_calibration_box_positions(
        self,
        calibration_boxes: list[CalibrationBoxModel]
    ) -> list[tuple[int, int]]:
        """
        Преобразует список CalibrationBox в список позиций (полка, место)
        """
        if not calibration_boxes:
            return []

        # 1. Извлекаем Y-центры для кластеризации
        y_centers = np.array(
            [(box.xyxy[1] + box.xyxy[3]) / 2 for box in calibration_boxes]
        ).reshape(-1, 1)

        # 2. Кластеризация по вертикали
        thresh = self._compute_distance_threshold(y_centers.flatten())
        clustering = AgglomerativeClustering(
            distance_threshold=thresh,
            n_clusters=None
        ).fit(y_centers)
        labels = clustering.labels_

        # 3. Группировка боксов по кластерам
        groups = defaultdict(list)
        for i, box in enumerate(calibration_boxes):
            groups[labels[i]].append(box)

        # 4. Сортировка полок сверху вниз
        sorted_groups = sorted(
            groups.values(),
            key=lambda boxes: np.mean([(box.xyxy[1]+box.xyxy[3])/2 for box in boxes])
        )
        
        # 5. Сортировка боксов внутри полки слева направо
        shelf_positions = []
        for shelf_boxes in sorted_groups:
            shelf_boxes_sorted = sorted(
                shelf_boxes,
                key=lambda box: (box.xyxy[0] + box.xyxy[2])/2
            )
            shelf_positions.append(shelf_boxes_sorted)

        # 6. Создание финальных позиций
        positions = []
        for box in calibration_boxes:
            for shelf_idx, shelf in enumerate(shelf_positions):
                if box in shelf:
                    position = shelf.index(box)
                    positions.append((shelf_idx, position))
                    break

        return positions