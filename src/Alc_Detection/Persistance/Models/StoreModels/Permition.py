from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, String
)
from Alc_Detection.Persistance.Models.BaseModel import BaseModel
from Alc_Detection.Persistance.Models.BaseStoreModel import BaseStoreModel
    
class Permition(BaseStoreModel):
    __tablename__ = "permitions"
        
    name = Column(String)
    
    post_permitions = relationship("PostPermition", back_populates="permition", cascade="all, delete-orphan", lazy='selectin')  