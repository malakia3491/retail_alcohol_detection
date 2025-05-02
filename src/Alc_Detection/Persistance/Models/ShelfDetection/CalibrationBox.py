from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, ForeignKey, Float
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class CalibrationBox(BaseModel):
    __tablename__ = "calibration_boxes"
    
    calibration_id = Column(UUID(as_uuid=True), ForeignKey("calibrations.id"))
    box_cords = Column(Vector(4))
    matrix_cords = Column(Vector(2))
    conf = Column(Float)
    
    calibration = relationship("Calibration", back_populates="calibration_boxes", lazy='selectin')