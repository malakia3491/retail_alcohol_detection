from sqlalchemy import Column, Sequence, String, Integer
from sqlalchemy.orm import relationship

from Alc_Detection.Persistance.Models.BaseStoreModel import BaseStoreModel
 
class Product(BaseStoreModel):
    __tablename__ = "products"
 
    name = Column(String)
    label = Column(
        Integer,
        Sequence("products_label_seq", start=1, increment=1),
        server_default=Sequence("products_label_seq").next_value(),
        unique=True,
        nullable=False,
    )
     
    planogram_products = relationship("PlanogramProduct", back_populates="product", lazy='selectin')
    images = relationship("ProductImage", back_populates="product", lazy='selectin')
    detections = relationship("RealogramDetection", foreign_keys="RealogramDetection.product_id", back_populates="product", lazy='selectin')
    incorrect_pos_detections = relationship("RealogramDetection", foreign_keys="RealogramDetection.right_product_id", back_populates="right_product", lazy='selectin')