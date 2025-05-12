from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, DateTime, String, ForeignKey, UUID
)

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class Incident(BaseModel):
    __tablename__ = "incidents"

    store_shift_id = Column(UUID(as_uuid=True), ForeignKey("store_shifts.id"))
    
    send_time = Column(DateTime)
    elimination_time = Column(DateTime, nullable=True)
    message = Column(String)
    type = Column(String)
    
    detections = relationship("RealogramDetection", back_populates="incident", lazy='selectin')
    store_shift = relationship("StoreShift", back_populates="incidents", lazy='selectin')
    persons = relationship("PersonIncident", back_populates="incident", cascade="all, delete-orphan", lazy='selectin')