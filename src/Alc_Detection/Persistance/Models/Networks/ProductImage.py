from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
 
class ProductImage(BaseModel):
    __tablename__ = "product_images"
 
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    
    path = Column(String)
    
    product = relationship("Product", back_populates="images", lazy='selectin')
    embeddings = relationship("Embedding", back_populates="image", cascade="all, delete-orphan", lazy='selectin')