from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class ShelvingPlanogramOrder(BaseModel):
    __tablename__ = "shelving_planogram_orders"
    
    planogram_order_id = Column(UUID(as_uuid=True), ForeignKey("planogram_orders.id"))
    shelving_id = Column(UUID(as_uuid=True), ForeignKey("shelvings.id"))
    
    planogram_order = relationship("PlanogramOrder", back_populates="shelving_planogram_orders", lazy='selectin')
    shelving = relationship("Shelving", back_populates="planogram_orders", lazy='selectin')
    planograms = relationship("Planogram", back_populates="shelving_planogram_order", lazy='selectin') 