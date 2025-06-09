from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, Time, ForeignKey, Integer
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
from Alc_Detection.Persistance.Models.BaseStoreModel import BaseStoreModel

class ShiftPost(BaseStoreModel):
    __tablename__ = "shift_posts"
    
    store_shift_id = Column(UUID(as_uuid=True), ForeignKey("store_shifts.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    count = Column(Integer)
    
    store_shift = relationship("StoreShift", back_populates="shift_posts", lazy='selectin')
    post = relationship("Post", back_populates="shift_posts", lazy='selectin')
    shift_post_persons = relationship("ShiftPostPerson", back_populates="shift_post", cascade="all, delete-orphan", lazy='selectin')  