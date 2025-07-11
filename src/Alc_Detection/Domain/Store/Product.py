import numpy as np

from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable, indexed
from Alc_Detection.Domain.NetworkModels.Image import Image

class Product(IndexNotifiable):
    def __init__(self, images: list[Image]=[], name: str="Unknown", label: int=0, retail_id:str=None, id=None): 
        super().__init__()
        self.id = id
        self._retail_id = retail_id
        self._name = name
        self._label = label
        self._images = images
        self._prototypes = self._compute_prototype_dict()

    @indexed
    @property
    def retail_id(self) -> str:
        return self._retail_id
    
    @retail_id.setter
    def retail_id(self, value: str):
        old = self._retail_id
        self._retail_id = value
        self._notify_index_changed('retail_id', old, value)

    @property 
    def name(self) -> str:
        return self._name

    @property
    def label(self) -> int:
        return self._label

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def image(self) -> Image:
        if len(self._images) == 0:
            return None
        return self._images[0]

    @property
    def is_classificated(self):
        return len(self._images) != 0

    def get_prototype(self, version) -> np.ndarray:
        if len(self._prototypes) == 0:
            return None
        if version in self._prototypes.keys():
            return self._prototypes[version]
        else: None
    
    def embeddings(self, version):
        embeddings = []
        for img in self._images:
            for emb in img.embeddings:
                if emb.model.version == version:
                    embeddings.append(emb.vector)     
        return embeddings
        
    def _compute_prototype_dict(self):
        embeddings = {}
        for img in self._images:
            for emb in img.embeddings:
                if not emb.model.version in embeddings:
                    embeddings[emb.model.version] = []
                embeddings[emb.model.version].append(emb.vector)       
        prototypes = {}
        for version in embeddings:
            prototypes[version] = np.mean(embeddings[version], axis=0)       
        return prototypes

    def add_images(self, *images: Image):  
        [self._images.append(img) for img in images]
        self._prototypes = self._compute_prototype_dict()
                              
    def copy(self) -> 'Product':
        images = [img.copy() for img in self._images]
        return Product(id=self.id,
                       retail_id=self.retail_id,
                       name=self.name,
                       images=images)
        
    def __eq__(self, value):
        return isinstance(value, Product) and \
               self.name == value.name
               
    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()