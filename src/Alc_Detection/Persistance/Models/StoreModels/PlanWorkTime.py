from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, DateTime
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class PlanWorkTime(BaseModel):
    __tablename__ = "plan_work_times"
    
    write_date = Column(DateTime, nullable=False)
    date_from = Column(DateTime, nullable=False)
    date_to = Column(DateTime, nullable=False)

    plan_days = relationship("PlanSchedule", back_populates="plan_work_time")