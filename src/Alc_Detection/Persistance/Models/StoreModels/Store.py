from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, String, Boolean
)

from Alc_Detection.Persistance.Models.BaseStoreModel import BaseStoreModel

class Store(BaseStoreModel):
    __tablename__ = "stores"
    
    login = Column(String, nullable=True, unique=True)
    password_hash = Column(String(128)) 
    
    name = Column(String, nullable=False)
    is_office = Column(Boolean, default=False)

    store_shifts = relationship("StoreShift", back_populates="store", cascade="all, delete-orphan", lazy='selectin')
    snapshots = relationship("RealogramSnapshot", back_populates="store", cascade="all, delete-orphan", lazy='selectin')
    calibrations = relationship("Calibration", back_populates="store", cascade="all, delete-orphan", lazy='selectin')