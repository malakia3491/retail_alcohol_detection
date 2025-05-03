from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, ForeignKey, String, DateTime, Integer, Float
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class RealogramSnapshot(BaseModel):
    __tablename__ = "realogram_snapshots"
    
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"))
    planogram_id = Column(UUID(as_uuid=True), ForeignKey("planograms.id"))
    shelving_id = Column(UUID(as_uuid=True), ForeignKey("shelvings.id"))
    datetime_upload = Column(DateTime)
    img_src = Column(String)
    empty_count = Column(Integer)
    planogram_accordance = Column(Float)
    
    planogram = relationship("Planogram", back_populates="realograms", lazy='selectin') 
    store = relationship("Store", back_populates="snapshots", lazy='selectin')
    shelving = relationship("Shelving", back_populates="snapshots", lazy='selectin')
    detections = relationship("RealogramDetection", back_populates="snapshot", cascade="all, delete-orphan", lazy='selectin')