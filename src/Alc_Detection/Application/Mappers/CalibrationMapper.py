from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Application.Mappers.PlanogramMapper import PlanogramMapper
from Alc_Detection.Domain.Shelf.Calibration import Calibration
from Alc_Detection.Domain.Shelf.ProductMatrix.CalibrationBox import CalibrationBox
from Alc_Detection.Persistance.Models.ShelfDetection.Calibration import Calibration as CalibrationModel

class CalibrationMapper:
    def __init__(self,
                 person_mapper: PersonMapper,
                 planogram_mapper: PlanogramMapper):
        self._planogram_mapper = planogram_mapper
        self._person_mapper = person_mapper

    def map_db_to_domain_model(self, db_model: CalibrationModel) -> Calibration:
        if db_model is None: return None
        if not isinstance(db_model, CalibrationModel):
            raise ValueError(db_model)
        person = self._person_mapper.map_to_domain_model(db_model.creator)
        planogram = self._planogram_mapper.map_to_domain_model(db_model.planogram)        
        calibration_boxes = [CalibrationBox(
                                xyxy=list(box.box_cords),
                                matrix_cords=list(box.matrix_cords),
                                conf=box.conf
                            ) 
                             for box in db_model.calibration_boxes]
        return Calibration(id = db_model.id,
                           date=db_model.calibration_date,
                           creator=person,
                           planogram=planogram,
                           calibration_boxes=calibration_boxes)
    
    def map_domain_to_db_model(self, domain_model: Calibration) -> CalibrationModel:
        pass