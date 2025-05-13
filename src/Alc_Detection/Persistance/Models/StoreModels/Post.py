from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, String, Boolean
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
from Alc_Detection.Persistance.Models.BaseStoreModel import BaseStoreModel

class Post(BaseStoreModel):
    __tablename__ = "posts"
    
    name = Column(String, nullable=False)

    shift_posts = relationship("ShiftPost", back_populates="post", cascade="all, delete-orphan", lazy='selectin')
    post_permitions = relationship("PostPermition", back_populates="post", cascade="all, delete-orphan", lazy='selectin')