from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, Time, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class ShiftPost(BaseModel):
    __tablename__ = "shift_posts"
    
    store_shift_id = Column(UUID(as_uuid=True), ForeignKey("store_shifts.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)

    store_shift = relationship("StoreShift", back_populates="shift_posts")
    post = relationship("Post", back_populates="shift_posts")
    shift_post_persons = relationship("ShiftPostPerson", back_populates="shift_post", cascade="all, delete-orphan")  