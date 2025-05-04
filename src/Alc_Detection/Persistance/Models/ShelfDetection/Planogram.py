from sqlalchemy import  UUID, Column, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
 
class Planogram(BaseModel):
    __tablename__ = "planograms"
    
    shelving_planogram_order_id = Column(UUID(as_uuid=True), ForeignKey("shelving_planogram_orders.id"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"))
    approver_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)
    upload_date = Column(DateTime)
    img_src = Column(String)
    approval_date = Column(DateTime, nullable=True)
    
    realograms = relationship("RealogramSnapshot", back_populates="planogram", lazy='selectin')
    shelving_planogram_order = relationship("ShelvingPlanogramOrder", back_populates="planograms", lazy='selectin', )
    author = relationship("Person",  foreign_keys=[author_id], back_populates="uploaded_planograms", lazy='selectin')
    approver = relationship("Person",  foreign_keys=[approver_id], back_populates="agreed_planograms", lazy='selectin')
    products = relationship("PlanogramProduct", back_populates="planogram", cascade="all, delete-orphan", lazy='selectin')
    calibrations = relationship("Calibration", back_populates="planogram", cascade="all, delete-orphan", lazy='selectin')