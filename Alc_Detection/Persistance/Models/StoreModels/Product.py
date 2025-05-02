from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
 
class Product(BaseModel):
    __tablename__ = "products"
 
    name = Column(String)
    label = Column(Integer, autoincrement=True, unique=True)
     
    planogram_products = relationship("PlanogramProduct", back_populates="product", lazy='selectin')
    images = relationship("ProductImage", back_populates="product", lazy='selectin')
    detections = relationship("RealogramDetection", back_populates="product", lazy='selectin')