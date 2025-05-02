from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, String, Time, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class StoreShift(BaseModel):
    __tablename__ = "store_shifts"
    
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    
    name = Column(String, nullable=False)
    time_work_start = Column(Time, nullable=False)
    time_work_end = Column(Time, nullable=False)
    time_break_start = Column(Time)
    time_break_end = Column(Time)

    store = relationship("Store", back_populates="store_shifts")
    incidents = relationship("Incident", back_populates="store_shift", cascade="all, delete-orphan")
    shift_posts = relationship("ShiftPost", back_populates="store_shift", cascade="all, delete-orphan")
    
    plan_days = relationship("PlanSchedule", back_populates="store_shift")
    
    