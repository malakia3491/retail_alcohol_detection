from sqlalchemy import  UUID, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
 
class PlanogramProduct(BaseModel):
    __tablename__ = "planogram_products"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    planogram_id = Column(UUID(as_uuid=True), ForeignKey("planograms.id", ondelete="CASCADE"))
    count = Column(Integer)
    
    product = relationship("Product", back_populates="planogram_products", lazy='selectin')
    planogram = relationship("Planogram", back_populates="products", lazy='selectin')
    boxes = relationship("ProductBox", back_populates="planogram_product", cascade="all, delete-orphan", lazy='selectin')