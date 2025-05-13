from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
from Alc_Detection.Persistance.Models.BaseStoreModel import BaseStoreModel
 
class Shelving(BaseStoreModel):
    __tablename__ = "shelvings"
    
    shelves_count = Column(Integer)
    name = Column(String)
    
    snapshots = relationship("RealogramSnapshot", back_populates="shelving")
    planogram_orders = relationship("ShelvingPlanogramOrder", back_populates="shelving")    