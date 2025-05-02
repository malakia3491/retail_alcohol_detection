from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
 
class EmbeddingModel(BaseModel):
    __tablename__ = "embedding_models"
 
    embedding_shape = Column(Integer)
    version = Column(String)
    path = Column(String)
    
    embeddings = relationship("Embedding", back_populates="model", cascade="all, delete-orphan", lazy='selectin')