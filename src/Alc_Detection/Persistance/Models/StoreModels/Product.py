from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
from Alc_Detection.Persistance.Models.BaseStoreModel import BaseStoreModel
 
class Product(BaseStoreModel):
    __tablename__ = "products"
 
    name = Column(String)
    label = Column(Integer, autoincrement=True, unique=True)
     
    planogram_products = relationship("PlanogramProduct", back_populates="product", lazy='selectin')
    images = relationship("ProductImage", back_populates="product", lazy='selectin')
    detections = relationship("RealogramDetection", foreign_keys="RealogramDetection.product_id", back_populates="product", lazy='selectin')
    incorrect_pos_detections = relationship("RealogramDetection", foreign_keys="RealogramDetection.right_product_id", back_populates="right_product", lazy='selectin')