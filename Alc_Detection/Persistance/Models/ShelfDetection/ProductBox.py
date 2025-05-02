from sqlalchemy import  UUID, Column, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
 
class ProductBox(BaseModel):
    __tablename__ = "product_boxes"
    
    planogram_product_id = Column(UUID(as_uuid=True), ForeignKey("planogram_products.id"))
    matrix_cords = Column(Vector(2))
    
    planogram_product = relationship("PlanogramProduct", back_populates="boxes", lazy='selectin')