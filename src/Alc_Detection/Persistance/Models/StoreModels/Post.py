from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, String, Boolean
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class Post(BaseModel):
    __tablename__ = "posts"
    
    name = Column(String, nullable=False)
    is_regular = Column(Boolean, nullable=False)
    is_administrative = Column(Boolean, nullable=False)

    shift_posts = relationship("ShiftPost", back_populates="post", cascade="all, delete-orphan", lazy='selectin')