from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, DateTime
)

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class ShiftAssignment(BaseModel):
    __tablename__ = "shift_assignments"
    
    assignment_date = Column(DateTime, nullable=False)

    shift_post_persons = relationship("ShiftPostPerson", back_populates="shift_assignment", cascade="all, delete-orphan", lazy='selectin')