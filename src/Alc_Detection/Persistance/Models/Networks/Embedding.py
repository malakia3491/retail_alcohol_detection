from sqlalchemy import  Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
 
class Embedding(BaseModel):
    __tablename__ = "embeddings"

    image_id = Column(UUID(as_uuid=True), ForeignKey("product_images.id", ondelete="CASCADE"))
    model_id = Column(UUID(as_uuid=True), ForeignKey("embedding_models.id", ondelete="CASCADE"))
 
    vector = Column(Vector(256))
        
    image = relationship("ProductImage", back_populates="embeddings", lazy='selectin')
    model = relationship("EmbeddingModel", back_populates="embeddings", lazy='selectin')