from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, ForeignKey, DateTime
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class Calibration(BaseModel):
    __tablename__ = "calibrations"
    
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"))
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"))
    planogram_id = Column(UUID(as_uuid=True), ForeignKey("planograms.id"))
    calibration_date = Column(DateTime)
    
    store = relationship("Store", back_populates="calibrations", lazy='selectin')
    creator = relationship("Person", back_populates="calibrations", lazy='selectin')
    planogram = relationship("Planogram", back_populates="calibrations", lazy='selectin')
    calibration_boxes = relationship("CalibrationBox", back_populates="calibration", cascade="all, delete-orphan", lazy='selectin')