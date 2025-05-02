from sqlalchemy import  UUID, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class PlanogramOrder(BaseModel):
    __tablename__ = "planogram_orders"
    
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"))
    order_date = Column(DateTime)
    dev_date = Column(DateTime)
    inc_date = Column(DateTime)
    
    shelving_planogram_orders = relationship("ShelvingPlanogramOrder", back_populates="planogram_order", cascade="all, delete-orphan", lazy='selectin')
    person = relationship("Person", back_populates="planogram_orders", lazy='selectin')