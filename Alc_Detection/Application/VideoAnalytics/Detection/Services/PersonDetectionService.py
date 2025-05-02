from torch.nn import Module
from torch import Tensor
from ultralytics.engine.results import Results 

from Alc_Detection.Application.VideoAnalytics.Interfaces.Detection import PersonsDetectionService
from Alc_Detection.Domain.Entities import *

class PersonDetectionService(PersonsDetectionService):
    def __init__(self,
                 detection_model: Module):
        self.detection_model = detection_model
        self.set_predict_settings()
    
    def set_predict_settings(self,
                             conf=0.6,
                             iou=0.45):
        self.conf = conf
        self.iou = iou
    
    def detect_persons_on(self, processed_img: Tensor) -> Results:
        results = self.detection_model.predict(
            source=processed_img,
            conf=self.conf,
            iou=self.iou,
            imgsz=640,
            save=False,
        )
        return results[0]