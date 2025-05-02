import torch
import torchvision
from ultralytics import YOLO

from Alc_Detection.Application.VideoAnalytics.Classification.Models.Classifiers.PrototypeClassifier import PrototypeClassifier
from Alc_Detection.Application.VideoAnalytics.Classification.Models.EmbeddingModels.EmbeddingNet import EmbeddingNet
from Alc_Detection.Application.VideoAnalytics.Classification.Models.EmbeddingModels.SiameseNetwork import SiameseNetwork
from Alc_Detection.Application.VideoAnalytics.Exceptions.Exceptions import ModelNotLoaded

class ModelLoader:
    def __init__(self, device, config_reader):
        self.device = device
        self.config_reader = config_reader
    
    def get_bottle_classifier(self):
        try:
            self.classifier = PrototypeClassifier(metric='cosine', device=self.device)
        except Exception:
            raise ModelNotLoaded("PrototypeClassifier", "")
        return self.classifier
    
    def get_bottle_detector(self, version):
        try:
            path = self.config_reader.get_model_path("bottle_detection", version)
            self.bottle_detector = YOLO(path).to(self.device)
        except Exception:
            raise ModelNotLoaded("bottle_detector", path)
        return self.bottle_detector
    
    def get_person_detector(self, version):
        try:
            path = self.config_reader.get_model_path("person_detection", version)
            self.person_detector = YOLO(path).to(self.device)
        except Exception as ex:
            raise ModelNotLoaded("person_detector", path)
        return self.person_detector
    
    def bottle_embedding_model(self, version):
        try:
            path = self.config_reader.get_model_path("embedding", version)
            embedding_net = EmbeddingNet(torchvision.models.resnet50(pretrained=True)).to(self.device)
            self.embedding_model = SiameseNetwork(embedding_net=embedding_net,
                                                  path=path,
                                                  version=version).to(self.device)
            self.embedding_model.load_state_dict(torch.load(path))
        except Exception:
            raise ModelNotLoaded("embedding_model", path)
        return self.embedding_model