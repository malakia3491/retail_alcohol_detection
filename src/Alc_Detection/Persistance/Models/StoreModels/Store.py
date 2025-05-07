from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, String, Boolean
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class Store(BaseModel):
    __tablename__ = "stores"
    
    name = Column(String, nullable=False)
    is_office = Column(Boolean, default=False)

    store_shifts = relationship("StoreShift", back_populates="store", cascade="all, delete-orphan", lazy='selectin')
    snapshots = relationship("RealogramSnapshot", back_populates="store", cascade="all, delete-orphan", lazy='selectin')
    calibrations = relationship("Calibration", back_populates="store", cascade="all, delete-orphan", lazy='selectin')