from datetime import datetime

from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Shelf.ProductMatrix.CalibrationBox import CalibrationBox

class Calibration:
    def __init__(self,
                 date: datetime,
                 creator: Person,
                 planogram: Planogram,
                 calibration_boxes: list[CalibrationBox],
                 id=None):
        self.id = id
        self._create_date = date
        self._creator = creator
        self._planogram = planogram
        self._calibrations_boxes = calibration_boxes
        
    @property
    def create_date(self) -> datetime:
        return self._create_date
    
    @property
    def creator(self) -> Person:
        return self._creator
    
    @property
    def planogram(self) -> Planogram:
        return self._planogram
    
    @property
    def calibrations_boxes(self) -> list[CalibrationBox]:
        return self._calibrations_boxes