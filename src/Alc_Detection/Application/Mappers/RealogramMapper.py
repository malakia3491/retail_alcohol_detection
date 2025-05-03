from Alc_Detection.Application.Mappers.PlanogramMapper import PlanogramMapper
from Alc_Detection.Application.Mappers.ProductMapper import ProductMapper
from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductMatrix import ProductMatrix
from Alc_Detection.Domain.Shelf.ProductMatrix.Shelf import Shelf
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Persistance.Models.Models import RealogramDetection as RealogramDetectionModel
from Alc_Detection.Persistance.Models.Models import RealogramSnapshot as RealogramSnapshotModel

class RealogramMapper:
    def __init__(
        self,
        planogram_mapper: PlanogramMapper,
        product_mapper: ProductMapper
    ):
        self._planogram_mapper = planogram_mapper
        self._product_mapper = product_mapper
        
    def map_to_domain_model(self, db_model: RealogramSnapshotModel) -> Realogram:
        if db_model is None: return None
        if not isinstance(db_model, RealogramSnapshotModel):
            raise ValueError(db_model)        
        boxes: dict[int, list[ProductBox]] = {}
        for detection in db_model.detections:
            shelf_id = int(detection.matrix_cords[0]) 
            if not shelf_id in boxes:
                boxes[shelf_id] = []
            product_box = ProductBox(
                id=detection.id,
                product=self._product_mapper.map_to_domain_model(detection.product),
                is_empty=detection.is_empty,
                is_incorrect_position=detection.is_incorrect_pos,
            ).load_positions_and_coordinates(
                xyxy=[detection.box_cords[0], detection.box_cords[1], detection.box_cords[2], detection.box_cords[3]],
                position=Point(detection.matrix_cords[0], detection.matrix_cords[1]),
                conf=detection.conf
            )
            boxes[shelf_id].append(product_box)
        shelves: dict[int, list[ProductBox]]= {}    
        for id, boxes_list in boxes.items():
            shelves[id] = Shelf(boxes=boxes_list)
        product_matrix = ProductMatrix(shelves=shelves)

        return Realogram(
            id=db_model.id,
            planogram=self._planogram_mapper.map_to_domain_model(db_model.planogram),
            product_matrix=product_matrix,
            create_date=db_model.datetime_upload,
            img_src=db_model.img_src,
        )