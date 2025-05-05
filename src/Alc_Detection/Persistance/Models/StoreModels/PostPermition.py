from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, ForeignKey, String
)
from Alc_Detection.Persistance.Models.BaseModel import BaseModel
    
class PostPermition(BaseModel):
    __tablename__ = "post_permitions"
        
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    permition_id = Column(UUID(as_uuid=True), ForeignKey("permitions.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String)
    
    post = relationship("Post", back_populates="post_permitions", lazy='selectin')
    permition =  relationship("Permition", back_populates="post_permitions", lazy='selectin')