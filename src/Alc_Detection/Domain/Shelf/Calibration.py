from datetime import datetime

from Alc_Detection.Application.Requests.Models import Planogram
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
        self.create_date = date
        self.creator = creator
        self.planogram = planogram
        self.calibrations_boxes = calibration_boxes