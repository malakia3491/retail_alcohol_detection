from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, String, ForeignKey, Boolean
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
    
class Person(BaseModel):
    __tablename__ = "persons"
    
    telegram_id = Column(String, unique=True)
    
    name = Column(String)
    is_worker = Column(Boolean)
    is_active = Column(Boolean, default=True)
    password_hash = Column(String(128)) 
    
    planogram_orders = relationship("PlanogramOrder", back_populates="person", cascade="all, delete-orphan", lazy='selectin')
    uploaded_planograms = relationship("Planogram", foreign_keys="Planogram.author_id", back_populates="author", cascade="all, delete-orphan", lazy='selectin')
    agreed_planograms = relationship("Planogram", foreign_keys="Planogram.approver_id", back_populates="approver", cascade="all, delete-orphan", lazy='selectin')
    shift_post_persons = relationship("ShiftPostPerson", back_populates="person", cascade="all, delete-orphan", lazy='selectin')
    calibrations = relationship("Calibration", back_populates="creator", cascade="all, delete-orphan", lazy='selectin')