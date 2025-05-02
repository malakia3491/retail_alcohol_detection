import numpy as np
from torch.nn import Module
from torch import Tensor
from ultralytics.engine.results import Results 
from ultralytics.engine.results import Boxes

from Alc_Detection.Application.VideoAnalytics.Interfaces.Detection import BottlesDetectionService
from Alc_Detection.Domain.Entities import *

class BottleModelDetectionService(BottlesDetectionService):
    def __init__(self,
                 detection_model: Module,
                 conf=0.6,
                 iou=0.45,
                 ):
        self.detection_model = detection_model
        self.conf = conf
        self.iou = iou
        self.set_predict_settings()
    
    def set_predict_settings(self,
                             conf=0.6,
                             iou=0.45):
        self.conf = conf
        self.iou = iou
    
    def detect_bottles_on(self, 
                          processed_img: Tensor,
    ) -> Results:
        results = self.detection_model.predict(
            source=processed_img,
            conf=self.conf,
            imgsz=640,
            iou=self.iou,
            save=False,
        )
        return results[0]