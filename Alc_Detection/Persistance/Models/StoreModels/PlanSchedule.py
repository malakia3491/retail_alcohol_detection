from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class PlanSchedule(BaseModel):
    __tablename__ = "plan_schedules"
    
    plan_work_time_id = Column(UUID(as_uuid=True), ForeignKey("plan_work_times.id"), nullable=False)
    store_shift_id = Column(UUID(as_uuid=True), ForeignKey("store_shifts.id"), nullable=False)
    
    date = Column(DateTime, nullable=False)

    plan_work_time = relationship("PlanWorkTime", back_populates="plan_days")
    store_shift = relationship("StoreShift", back_populates="plan_days")