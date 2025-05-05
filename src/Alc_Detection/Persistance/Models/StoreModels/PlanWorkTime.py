from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class PlanWorkTime(BaseModel):
    __tablename__ = "plan_work_times"
    
    store_shift_id = Column(UUID(as_uuid=True), ForeignKey("store_shifts.id"), nullable=False)
    write_date = Column(DateTime, nullable=False)
    date_from = Column(DateTime, nullable=False)
    date_to = Column(DateTime, nullable=False)

    plan_days = relationship("PlanSchedule", back_populates="plan_work_time", cascade="all, delete-orphan", lazy='selectin')
    store_shift = relationship("StoreShift", back_populates="schedules", lazy='selectin')