from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, DateTime, ForeignKey, Boolean, Float
)
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class RealogramDetection(BaseModel):
    __tablename__ = "realogram_detections"
    
    realogram_id = Column(UUID(as_uuid=True), ForeignKey("realogram_snapshots.id"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    right_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    
    matrix_cords = Column(Vector(2))
    box_cords = Column(Vector(4))
    is_empty = Column(Boolean)
    conf = Column(Float)
    is_incorrect_pos = Column(Boolean)
    elimination_time = Column(DateTime, nullable=True)
    
    snapshot = relationship("RealogramSnapshot", back_populates="detections", lazy='selectin')
    incident = relationship("Incident", back_populates="detections", lazy='selectin')
    product = relationship("Product",  foreign_keys=[product_id], back_populates="detections", lazy='selectin')
    right_product = relationship("Product", foreign_keys=[right_product_id], back_populates="incorrect_pos_detections", lazy='selectin')