from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, ForeignKey, Date
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class ShiftPostPerson(BaseModel):
    __tablename__ = "shift_post_persons"
    
    shift_post_id = Column(UUID(as_uuid=True), ForeignKey("shift_posts.id"), nullable=False)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False)
    shift_assignment_id = Column(UUID(as_uuid=True), ForeignKey("shift_assignments.id"), nullable=False)

    shift_post = relationship("ShiftPost", back_populates="shift_post_persons")
    person = relationship("Person", back_populates="shift_post_persons")    
    shift_assignment = relationship("ShiftAssignment", back_populates="shift_post_persons")